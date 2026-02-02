"""
Test automatic YouTube playlist fetching
"""

from services.youtube_service import YouTubePlaylistService
import json

def test_auto_fetch():
    """Test automatic playlist video fetching"""
    
    service = YouTubePlaylistService("./test_data")
    
    # Test with a sample playlist (use a small public playlist)
    test_playlist_url = "https://www.youtube.com/playlist?list=PLWKjhJtqVAbnqBxcdjVGgT3uVR10bzTEB"  # Python tutorials
    
    print("🔄 Testing automatic playlist fetching...")
    print(f"URL: {test_playlist_url}\n")
    
    try:
        # Fetch playlist with videos
        playlist_data = service.fetch_playlist_videos(
            test_playlist_url,
            title="Test Python Playlist",
            description="Testing auto-fetch functionality"
        )
        
        print("✅ Playlist fetched successfully!\n")
        print(f"📺 Title: {playlist_data['title']}")
        print(f"📝 Description: {playlist_data.get('description', 'N/A')[:100]}...")
        print(f"🎥 Videos: {playlist_data['video_count']}")
        print(f"🔧 Method: {playlist_data['fetch_method']}")
        print(f"👤 Channel: {playlist_data.get('channel', 'N/A')}\n")
        
        if playlist_data['videos']:
            print("📋 First 3 videos:")
            for video in playlist_data['videos'][:3]:
                print(f"  {video['order']}. {video['title']}")
                print(f"     ID: {video['video_id']}")
                print(f"     URL: {video['video_url']}")
                print()
        
        # Save to file for inspection
        with open('test_playlist_data.json', 'w', encoding='utf-8') as f:
            json.dump(playlist_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Test data saved to: test_playlist_data.json")
        print("\n🎉 Auto-fetch is working correctly!")
        
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        print("Install yt-dlp: pip install yt-dlp")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auto_fetch()
