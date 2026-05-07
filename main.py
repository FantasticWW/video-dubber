"""
Video Dubbing App - Kivy Android App
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.video import Video
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.logger import Logger

import os
import json
from datetime import datetime

try:
    from jnius import autoclass
    IS_ANDROID = True
    Logger.info("Running on Android platform - jnius available")

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    mActivity = PythonActivity.mActivity
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')

    try:
        from android.permissions import request_permissions, Permission
        HAS_PERMISSIONS = True
    except ImportError:
        HAS_PERMISSIONS = False
        Logger.warning("android.permissions not available")

    try:
        from android.activity import bind_activity_result
        HAS_ACTIVITY_RESULT = True
    except ImportError:
        HAS_ACTIVITY_RESULT = False
        Logger.warning("android.activity.bind_activity_result not available")
except ImportError:
    IS_ANDROID = False
    HAS_PERMISSIONS = False
    HAS_ACTIVITY_RESULT = False
    Logger.info("Not running on Android platform")

try:
    from plyer import audio
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False
    Logger.warning("Plyer audio not available")


class VideoListItem(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    video_path = StringProperty('')
    video_name = StringProperty('')

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.video_path = data.get('path', '')
        self.video_name = data.get('name', '')
        self.selected = data.get('selected', False)
        return super().refresh_view_attrs(rv, index, data)


class VideoRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = 'VideoListItem'
        self.data = []


class VideoDubberApp(App):
    video_list = ListProperty([])
    current_video_index = -1
    is_recording = BooleanProperty(False)
    current_audio_path = StringProperty('')
    permissions_granted = False
    REQUEST_CODE_PICK_VIDEO = 1001

    def build(self):
        self.title = 'Video Dubber'

        if IS_ANDROID:
            Clock.schedule_once(self.request_android_permissions, 0)

        self.load_video_list()

        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_add = Button(text='Add Video')
        btn_add.bind(on_press=self.add_videos)
        btn_clear = Button(text='Clear List')
        btn_clear.bind(on_press=self.clear_videos)
        btn_layout.add_widget(btn_add)
        btn_layout.add_widget(btn_clear)

        list_label = Label(text='Video List', size_hint_y=None, height=30,
                          halign='left', text_size=(None, None))
        list_label.bind(size=list_label.setter('text_size'))

        self.video_rv = VideoRecycleView()
        self.video_rv.data = [{'name': v['name'], 'path': v['path'], 'selected': False}
                             for v in self.video_list]

        player_layout = BoxLayout(size_hint_y=0.4, orientation='vertical')
        player_label = Label(text='Video Player', size_hint_y=None, height=30)
        self.video_widget = Video(options={'allow_stretch': True}, state='stop')
        self.video_widget.bind(position=self.on_video_position)
        player_layout.add_widget(player_label)
        player_layout.add_widget(self.video_widget)

        dub_layout = BoxLayout(size_hint_y=None, height=80, spacing=10, orientation='vertical')
        dub_btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        self.btn_record = Button(text='Start Dub')
        self.btn_record.bind(on_press=self.toggle_recording)
        self.btn_play_audio = Button(text='Play Audio')
        self.btn_play_audio.bind(on_press=self.play_recorded_audio)
        self.btn_save = Button(text='Save')
        self.btn_save.bind(on_press=self.save_dubbed_video)
        dub_btn_layout.add_widget(self.btn_record)
        dub_btn_layout.add_widget(self.btn_play_audio)
        dub_btn_layout.add_widget(self.btn_save)
        self.status_label = Label(text='Select a video to dub', size_hint_y=None, height=30)
        dub_layout.add_widget(dub_btn_layout)
        dub_layout.add_widget(self.status_label)

        root.add_widget(btn_layout)
        root.add_widget(list_label)
        root.add_widget(self.video_rv)
        root.add_widget(player_layout)
        root.add_widget(dub_layout)

        return root

    def request_android_permissions(self, dt):
        if not IS_ANDROID or not HAS_PERMISSIONS:
            Logger.info("Permissions not available on this platform")
            self.permissions_granted = True
            return
        try:
            permissions = [
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.RECORD_AUDIO
            ]
            request_permissions(permissions, self.on_permissions_result)
            Logger.info("Permission request sent")
        except Exception as e:
            Logger.error(f"Permission request error: {e}")
            self.permissions_granted = True

    def on_permissions_result(self, permissions, results):
        Logger.info(f"Permissions result: {permissions}, {results}")
        self.permissions_granted = all(results)

    def add_videos(self, instance):
        if IS_ANDROID:
            try:
                intent = Intent(Intent.ACTION_GET_CONTENT)
                intent.setType('video/*')
                intent.addCategory(Intent.CATEGORY_OPENABLE)
                if HAS_ACTIVITY_RESULT:
                    bind_activity_result(self.on_activity_result)
                mActivity.startActivityForResult(intent, self.REQUEST_CODE_PICK_VIDEO)
                self.status_label.text = 'Select a video file...'
            except Exception as e:
                Logger.error(f"Intent error: {e}")
                self.status_label.text = f'Failed to open picker: {str(e)}'
        else:
            self.status_label.text = 'Run on Android device'

    def on_activity_result(self, requestCode, resultCode, data):
        Logger.info(f"Activity result: requestCode={requestCode}, resultCode={resultCode}")
        if requestCode == self.REQUEST_CODE_PICK_VIDEO and resultCode == -1:
            if data:
                uri = data.getData()
                if uri:
                    Logger.info(f"Selected URI: {uri}")
                    path = self.get_real_path_from_uri(uri)
                    if path:
                        self.add_video_to_list(path)

    def get_real_path_from_uri(self, uri):
        try:
            cursor = mActivity.getContentResolver().query(uri, None, None, None, None)
            if cursor:
                cursor.moveToFirst()
                path_index = cursor.getColumnIndex('_data')
                if path_index >= 0:
                    path = cursor.getString(path_index)
                    cursor.close()
                    return path
                cursor.close()
            return uri.toString()
        except Exception as e:
            Logger.error(f"Get path from uri error: {e}")
            return uri.toString() if uri else None

    def add_video_to_list(self, path):
        try:
            name = os.path.basename(path) if path and '/' in path else str(path)
            if path:
                self.video_list.append({
                    'name': name,
                    'path': path,
                    'selected': False
                })
                self.update_video_list_view()
                self.save_video_list()
                self.status_label.text = f'Added: {name}'
        except Exception as e:
            Logger.error(f"Add video error: {e}")

    def clear_videos(self, instance):
        try:
            self.video_list = []
            self.current_video_index = -1
            self.video_widget.state = 'stop'
            self.video_widget.source = ''
            self.update_video_list_view()
            self.save_video_list()
            self.status_label.text = 'List cleared'
        except Exception as e:
            Logger.error(f"Clear videos error: {e}")

    def update_video_list_view(self):
        try:
            self.video_rv.data = [{'name': v['name'], 'path': v['path'], 'selected': i == self.current_video_index}
                                 for i, v in enumerate(self.video_list)]
        except Exception as e:
            Logger.error(f"Update list view error: {e}")

    def select_video(self, index):
        try:
            if 0 <= index < len(self.video_list):
                self.current_video_index = index
                video = self.video_list[index]
                self.video_widget.source = video['path']
                self.video_widget.state = 'play'
                self.update_video_list_view()
                self.status_label.text = f'Playing: {video["name"]}'
        except Exception as e:
            Logger.error(f"Select video error: {e}")
            self.status_label.text = 'Failed to play video'

    def on_video_position(self, instance, value):
        pass

    def toggle_recording(self, instance):
        if self.current_video_index < 0:
            self.status_label.text = 'Please select a video first'
            return

        if IS_ANDROID and not self.permissions_granted:
            self.status_label.text = 'Please grant recording permission'
            self.request_android_permissions(0)
            return

        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        if HAS_AUDIO:
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                self.current_audio_path = os.path.join(
                    self.get_storage_path(),
                    f'dubbing_{timestamp}.wav'
                )
                audio.start_recording(self.current_audio_path)
                self.is_recording = True
                self.btn_record.text = 'Stop Dub'
                self.status_label.text = 'Dubbing...'
            except Exception as e:
                Logger.error(f"Recording error: {e}")
                self.status_label.text = 'Recording failed'
        else:
            self.status_label.text = 'Recording not available'

    def stop_recording(self):
        if HAS_AUDIO:
            try:
                audio.stop_recording()
                self.is_recording = False
                self.btn_record.text = 'Start Dub'
                if self.current_audio_path:
                    self.status_label.text = 'Dub saved'
                else:
                    self.status_label.text = 'Dub completed'
            except Exception as e:
                Logger.error(f"Stop recording error: {e}")
                self.is_recording = False
                self.btn_record.text = 'Start Dub'
                self.status_label.text = 'Failed to stop recording'

    def play_recorded_audio(self, instance):
        try:
            if self.current_audio_path and os.path.exists(self.current_audio_path):
                sound = SoundLoader.load(self.current_audio_path)
                if sound:
                    sound.play()
                    self.status_label.text = 'Playing dub audio...'
                else:
                    self.status_label.text = 'Cannot load audio'
            else:
                self.status_label.text = 'No dub to play'
        except Exception as e:
            Logger.error(f"Play audio error: {e}")
            self.status_label.text = 'Failed to play audio'

    def merge_audio_with_video(self, video_path, audio_path, output_path):
        """Use FFmpeg to replace video audio track with recorded audio"""
        try:
            import subprocess
            Logger.info(f"FFmpeg merge: video={video_path}, audio={audio_path}, output={output_path}")

            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-map', '0:v',
                '-map', '1:a',
                '-shortest',
                '-y',
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            Logger.info(f"FFmpeg return code: {result.returncode}")
            if result.stderr:
                Logger.info(f"FFmpeg stderr: {result.stderr[:500]}")

            return result.returncode == 0
        except subprocess.TimeoutExpired:
            Logger.error("FFmpeg merge timeout")
            return False
        except Exception as e:
            Logger.error(f"FFmpeg merge error: {e}")
            return False

    def save_dubbed_video(self, instance):
        if self.current_video_index < 0:
            self.status_label.text = 'Please select a video first'
            return

        if not self.current_audio_path or not os.path.exists(self.current_audio_path):
            self.status_label.text = 'Please record dub first'
            return

        video = self.video_list[self.current_video_index]
        video_path = video['path']

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.get_storage_path(),
            f'dubbed_{timestamp}.mp4'
        )

        self.status_label.text = 'Merging audio with video...'

        success = self.merge_audio_with_video(video_path, self.current_audio_path, output_path)

        if success and os.path.exists(output_path):
            self.status_label.text = f'Saved: {os.path.basename(output_path)}'
            self.add_video_to_list(output_path)
        else:
            self.status_label.text = 'Failed to merge video'

    def get_storage_path(self):
        try:
            if IS_ANDROID:
                external_storage = os.path.join('/sdcard', 'VideoDubber')
                if not os.path.exists(external_storage):
                    os.makedirs(external_storage)
                return external_storage
            elif hasattr(self, 'user_data_dir'):
                return self.user_data_dir
            else:
                return os.path.expanduser('~')
        except Exception as e:
            Logger.error(f"Get storage path error: {e}")
            return os.path.expanduser('~')

    def save_video_list(self):
        try:
            data_path = os.path.join(self.get_storage_path(), 'video_list.json')
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(self.video_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            Logger.error(f"Save video list error: {e}")

    def load_video_list(self):
        try:
            data_path = os.path.join(self.get_storage_path(), 'video_list.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.video_list = json.load(f)
        except Exception as e:
            Logger.error(f"Load video list error: {e}")
            self.video_list = []


if __name__ == '__main__':
    VideoDubberApp().run()