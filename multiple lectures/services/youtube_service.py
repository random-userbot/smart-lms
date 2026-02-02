"""
YouTube Playlist Service
Handles YouTube playlist fetching and management for courses
"""

import re
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import logging

# Try yt-dlp first (more features)
YT_DLP_AVAILABLE = False
PYTUBE_AVAILABLE = False

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
    logging.info("yt-dlp loaded successfully")
except ImportError as e:
    logging.info(f"yt-dlp not available: {e}")
except Exception as e:
    logging.warning(f"Error loading yt-dlp: {e}")
    
try:
    import pytube
    from pytube import Playlist, YouTube
    PYTUBE_AVAILABLE = True
    logging.info(f"pytube loaded successfully (version: {pytube.__version__})")
except ImportError as e:
    logging.info(f"pytube not available: {e}")
except Exception as e:
    logging.warning(f"Error loading pytube: {e}")

if not YT_DLP_AVAILABLE and not PYTUBE_AVAILABLE:
    logging.warning("Neither yt-dlp nor pytube installed. Auto-fetch not available. Install with: pip install pytube")

AUTO_FETCH_AVAILABLE = YT_DLP_AVAILABLE or PYTUBE_AVAILABLE
logging.info(f"Auto-fetch available: {AUTO_FETCH_AVAILABLE} (yt-dlp: {YT_DLP_AVAILABLE}, pytube: {PYTUBE_AVAILABLE})")


class YouTubePlaylistService:
    """Service to manage YouTube playlists for courses"""
    
    def __init__(self, storage_dir: str = "./data"):
        self.storage_dir = storage_dir
        self.playlists_file = os.path.join(storage_dir, "youtube_playlists.json")
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Create storage directory and files if they don't exist"""
        os.makedirs(self.storage_dir, exist_ok=True)
        if not os.path.exists(self.playlists_file):
            self._write_json({})
    
    def _read_json(self) -> Dict:
        """Read playlists from JSON file"""
        try:
            with open(self.playlists_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _write_json(self, data: Dict):
        """Write playlists to JSON file"""
        with open(self.playlists_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def extract_playlist_id(self, url: str) -> Optional[str]:
        """
        Extract playlist ID from YouTube URL
        
        Supported formats:
        - https://www.youtube.com/playlist?list=PLxxxxxx
        - https://youtube.com/playlist?list=PLxxxxxx
        - PLxxxxxx (direct ID)
        
        Args:
            url: YouTube playlist URL or ID
        
        Returns:
            Playlist ID or None if invalid
        """
        if not url:
            return None
        
        # Direct ID (starts with PL, UU, etc.)
        if re.match(r'^[A-Z]{2}[\w-]{32,}$', url):
            return url
        
        # Extract from URL
        patterns = [
            r'[?&]list=([A-Z]{2}[\w-]{32,})',
            r'youtube\.com/playlist\?list=([A-Z]{2}[\w-]{32,})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def parse_playlist_manual(self, playlist_url: str, title: str, description: str = "") -> Dict:
        """
        Parse playlist information manually (without API)
        
        Args:
            playlist_url: YouTube playlist URL
            title: Playlist title (user provided)
            description: Playlist description (optional)
        
        Returns:
            Playlist data dictionary
        """
        playlist_id = self.extract_playlist_id(playlist_url)
        
        if not playlist_id:
            raise ValueError("Invalid YouTube playlist URL")
        
        # For manual mode, we'll store the playlist URL and let iframe handle it
        return {
            'playlist_id': playlist_id,
            'title': title,
            'description': description,
            'playlist_url': f"https://www.youtube.com/playlist?list={playlist_id}",
            'video_count': 0,  # Will be populated when videos are added manually
            'videos': [],  # Videos will be added manually by teacher
            'created_at': datetime.utcnow().isoformat(),
            'fetch_method': 'manual'
        }
    
    def fetch_playlist_videos(self, playlist_url: str, title: str = None, description: str = "") -> Dict:
        """
        Automatically fetch playlist and all videos using yt-dlp or pytube
        
        Args:
            playlist_url: YouTube playlist URL
            title: Playlist title (optional - will use YouTube title if not provided)
            description: Playlist description (optional)
        
        Returns:
            Playlist data dictionary with videos
        """
        if not AUTO_FETCH_AVAILABLE:
            raise ImportError("Neither yt-dlp nor pytube is installed. Install one with: pip install yt-dlp OR pip install pytube")
        
        playlist_id = self.extract_playlist_id(playlist_url)
        if not playlist_id:
            raise ValueError("Invalid YouTube playlist URL")
        
        # Try pytube first (simpler and more reliable for basic playlists)
        if PYTUBE_AVAILABLE:
            try:
                return self._fetch_with_pytube(playlist_url, playlist_id, title, description)
            except Exception as e:
                logging.warning(f"pytube failed: {e}, trying yt-dlp...")
                if not YT_DLP_AVAILABLE:
                    raise
        
        # Fallback to yt-dlp
        if YT_DLP_AVAILABLE:
            return self._fetch_with_ytdlp(playlist_url, playlist_id, title, description)
        
        raise RuntimeError("Could not fetch playlist with any available library")
    
    def _fetch_with_pytube(self, playlist_url: str, playlist_id: str, title: str = None, description: str = "") -> Dict:
        """Fetch playlist using pytube library"""
        from pytube import Playlist, YouTube
        
        try:
            pl = Playlist(playlist_url)
            
            # Use provided title or YouTube title
            playlist_title = title or pl.title or 'Untitled Playlist'
            
            # Extract videos
            videos = []
            for idx, video_url in enumerate(pl.video_urls[:100], start=1):  # Limit to 100 videos
                try:
                    yt = YouTube(video_url)
                    video_id = yt.video_id
                    
                    videos.append({
                        'video_id': video_id,
                        'title': yt.title or f'Video {idx}',
                        'description': (yt.description or '')[:500] if yt.description else '',
                        'video_url': f"https://www.youtube.com/watch?v={video_id}",
                        'order': idx,
                        'duration': yt.length if hasattr(yt, 'length') else 0,
                        'materials': [],
                        'added_at': datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logging.warning(f"Failed to fetch video {idx}: {e}")
                    continue
            
            return {
                'playlist_id': playlist_id,
                'title': playlist_title,
                'description': description or pl.description or '',
                'playlist_url': f"https://www.youtube.com/playlist?list={playlist_id}",
                'video_count': len(videos),
                'videos': videos,
                'created_at': datetime.utcnow().isoformat(),
                'fetch_method': 'automatic_pytube',
                'channel': pl.owner or '',
                'channel_url': pl.owner_url or ''
            }
        
        except Exception as e:
            logging.error(f"Error fetching playlist with pytube: {e}")
            raise ValueError(f"Could not fetch playlist: {str(e)}")
    
    def _fetch_with_ytdlp(self, playlist_url: str, playlist_id: str, title: str = None, description: str = "") -> Dict:
        """Fetch playlist using yt-dlp library"""
        import yt_dlp
        
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # Don't download, just extract metadata
                'playlist_items': '1-100',  # Limit to first 100 videos
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract playlist info
                info = ydl.extract_info(playlist_url, download=False)
                
                if not info or 'entries' not in info:
                    raise ValueError("Could not extract playlist information")
                
                # Use provided title or YouTube title
                playlist_title = title or info.get('title', 'Untitled Playlist')
                
                # Extract videos
                videos = []
                for idx, entry in enumerate(info['entries'], start=1):
                    if entry:  # Some entries might be None
                        video_id = entry.get('id')
                        if video_id:
                            videos.append({
                                'video_id': video_id,
                                'title': entry.get('title', f'Video {idx}'),
                                'description': entry.get('description', '')[:500] if entry.get('description') else '',
                                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                                'order': idx,
                                'duration': entry.get('duration', 0),
                                'materials': [],
                                'added_at': datetime.utcnow().isoformat()
                            })
                
                return {
                    'playlist_id': playlist_id,
                    'title': playlist_title,
                    'description': description or info.get('description', ''),
                    'playlist_url': f"https://www.youtube.com/playlist?list={playlist_id}",
                    'video_count': len(videos),
                    'videos': videos,
                    'created_at': datetime.utcnow().isoformat(),
                    'fetch_method': 'automatic',
                    'channel': info.get('uploader', ''),
                    'channel_url': info.get('uploader_url', '')
                }
        
        except Exception as e:
            logging.error(f"Error fetching playlist: {e}")
            # Fallback to manual mode
            raise ValueError(f"Could not automatically fetch playlist: {str(e)}. You can add videos manually instead.")
    
    def add_video_to_playlist(self, course_id: str, playlist_id: str, 
                             video_url: str, title: str, 
                             description: str = "", order: int = None) -> bool:
        """
        Add a video to a playlist manually
        
        Args:
            course_id: Course ID
            playlist_id: Playlist ID
            video_url: YouTube video URL
            title: Video title
            description: Video description
            order: Video order in playlist (auto-increment if None)
        
        Returns:
            Success status
        """
        playlists = self._read_json()
        
        course_key = f"course_{course_id}"
        if course_key not in playlists:
            return False
        
        # Find the playlist
        playlist_found = False
        for playlist in playlists[course_key]:
            if playlist['playlist_id'] == playlist_id:
                playlist_found = True
                
                # Extract video ID
                video_id = self.extract_video_id(video_url)
                if not video_id:
                    return False
                
                # Check if video already exists
                existing_ids = [v['video_id'] for v in playlist['videos']]
                if video_id in existing_ids:
                    return False
                
                # Determine order
                if order is None:
                    order = len(playlist['videos']) + 1
                
                # Add video
                video_data = {
                    'video_id': video_id,
                    'title': title,
                    'description': description,
                    'video_url': f"https://www.youtube.com/watch?v={video_id}",
                    'order': order,
                    'materials': [],  # Study materials attached to this video
                    'added_at': datetime.utcnow().isoformat()
                }
                
                playlist['videos'].append(video_data)
                playlist['videos'].sort(key=lambda x: x['order'])
                playlist['video_count'] = len(playlist['videos'])
                break
        
        if not playlist_found:
            return False
        
        self._write_json(playlists)
        return True
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL
        
        Supported formats:
        - https://www.youtube.com/watch?v=xxxxxxxxxxx
        - https://youtu.be/xxxxxxxxxxx
        - xxxxxxxxxxx (direct ID)
        
        Args:
            url: YouTube video URL or ID
        
        Returns:
            Video ID or None if invalid
        """
        if not url:
            return None
        
        # Direct ID (11 characters)
        if re.match(r'^[\w-]{11}$', url):
            return url
        
        # Extract from URL
        patterns = [
            r'(?:v=|/)([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'embed/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def add_playlist_to_course(self, course_id: str, playlist_data: Dict) -> bool:
        """
        Add a playlist to a course
        
        Args:
            course_id: Course ID
            playlist_data: Playlist information dictionary
        
        Returns:
            Success status
        """
        playlists = self._read_json()
        
        course_key = f"course_{course_id}"
        if course_key not in playlists:
            playlists[course_key] = []
        
        # Check if playlist already exists for this course
        existing_ids = [p['playlist_id'] for p in playlists[course_key]]
        if playlist_data['playlist_id'] in existing_ids:
            return False
        
        playlists[course_key].append(playlist_data)
        self._write_json(playlists)
        return True
    
    def get_course_playlists(self, course_id: str) -> List[Dict]:
        """
        Get all playlists for a course
        
        Args:
            course_id: Course ID
        
        Returns:
            List of playlist dictionaries
        """
        playlists = self._read_json()
        course_key = f"course_{course_id}"
        return playlists.get(course_key, [])
    
    def get_playlist(self, course_id: str, playlist_id: str) -> Optional[Dict]:
        """
        Get a specific playlist
        
        Args:
            course_id: Course ID
            playlist_id: Playlist ID
        
        Returns:
            Playlist dictionary or None
        """
        playlists = self.get_course_playlists(course_id)
        for playlist in playlists:
            if playlist['playlist_id'] == playlist_id:
                return playlist
        return None
    
    def attach_material_to_video(self, course_id: str, playlist_id: str, 
                                video_id: str, material: Dict) -> bool:
        """
        Attach study material to a specific video
        
        Args:
            course_id: Course ID
            playlist_id: Playlist ID
            video_id: Video ID
            material: Material dictionary with keys:
                     - material_id
                     - title
                     - type (pdf, pptx, docx, etc.)
                     - file_path
                     - file_name
        
        Returns:
            Success status
        """
        playlists = self._read_json()
        course_key = f"course_{course_id}"
        
        if course_key not in playlists:
            return False
        
        # Find playlist and video
        for playlist in playlists[course_key]:
            if playlist['playlist_id'] == playlist_id:
                for video in playlist['videos']:
                    if video['video_id'] == video_id:
                        # Add material
                        material['attached_at'] = datetime.utcnow().isoformat()
                        video['materials'].append(material)
                        self._write_json(playlists)
                        return True
        
        return False
    
    def remove_material_from_video(self, course_id: str, playlist_id: str,
                                   video_id: str, material_id: str) -> bool:
        """
        Remove study material from a video
        
        Args:
            course_id: Course ID
            playlist_id: Playlist ID
            video_id: Video ID
            material_id: Material ID to remove
        
        Returns:
            Success status
        """
        playlists = self._read_json()
        course_key = f"course_{course_id}"
        
        if course_key not in playlists:
            return False
        
        # Find and remove material
        for playlist in playlists[course_key]:
            if playlist['playlist_id'] == playlist_id:
                for video in playlist['videos']:
                    if video['video_id'] == video_id:
                        video['materials'] = [
                            m for m in video['materials'] 
                            if m['material_id'] != material_id
                        ]
                        self._write_json(playlists)
                        return True
        
        return False
    
    def delete_playlist(self, course_id: str, playlist_id: str) -> bool:
        """
        Delete a playlist from a course
        
        Args:
            course_id: Course ID
            playlist_id: Playlist ID
        
        Returns:
            Success status
        """
        playlists = self._read_json()
        course_key = f"course_{course_id}"
        
        if course_key not in playlists:
            return False
        
        original_count = len(playlists[course_key])
        playlists[course_key] = [
            p for p in playlists[course_key] 
            if p['playlist_id'] != playlist_id
        ]
        
        if len(playlists[course_key]) < original_count:
            self._write_json(playlists)
            return True
        
        return False
    
    def update_video_order(self, course_id: str, playlist_id: str,
                          video_id: str, new_order: int) -> bool:
        """
        Update video order in playlist
        
        Args:
            course_id: Course ID
            playlist_id: Playlist ID
            video_id: Video ID
            new_order: New order position
        
        Returns:
            Success status
        """
        playlists = self._read_json()
        course_key = f"course_{course_id}"
        
        if course_key not in playlists:
            return False
        
        for playlist in playlists[course_key]:
            if playlist['playlist_id'] == playlist_id:
                for video in playlist['videos']:
                    if video['video_id'] == video_id:
                        video['order'] = new_order
                
                # Re-sort videos
                playlist['videos'].sort(key=lambda x: x['order'])
                self._write_json(playlists)
                return True
        
        return False


# Singleton instance
_youtube_service = None

def get_youtube_service() -> YouTubePlaylistService:
    """Get or create YouTube playlist service instance"""
    global _youtube_service
    if _youtube_service is None:
        _youtube_service = YouTubePlaylistService()
    return _youtube_service
