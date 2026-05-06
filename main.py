"""
视频配音应用 - Kivy Android App
功能：本地上传多个视频，选择视频边播放边配音
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.logger import Logger

import os
import json
from datetime import datetime

try:
    from plyer import filechooser, audio
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False
    Logger.warning("Plyer not available, using fallback methods")


class VideoListItem(RecycleDataViewBehavior, BoxLayout):
    """视频列表项"""
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

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            app = App.get_running_app()
            app.root.select_video(self.index)
            return True
        return super().on_touch_down(touch)


class VideoRecycleView(RecycleView):
    """视频列表视图"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = 'VideoListItem'
        self.data = []


class VideoDubberApp(App):
    """主应用"""
    video_list = ListProperty([])
    current_video_index = -1
    is_recording = BooleanProperty(False)
    current_audio_path = StringProperty('')

    def build(self):
        self.title = '视频配音工具'
        self.load_video_list()

        # 主布局
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 顶部按钮区
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        btn_add = Button(text='添加视频', font_name='SimHei')
        btn_add.bind(on_press=self.add_videos)

        btn_clear = Button(text='清空列表', font_name='SimHei')
        btn_clear.bind(on_press=self.clear_videos)

        btn_layout.add_widget(btn_add)
        btn_layout.add_widget(btn_clear)

        # 视频列表区域
        list_label = Label(text='视频列表', size_hint_y=None, height=30,
                          font_name='SimHei', halign='left', text_size=(None, None))
        list_label.bind(size=list_label.setter('text_size'))

        self.video_rv = VideoRecycleView()
        self.video_rv.data = [{'name': v['name'], 'path': v['path'], 'selected': False}
                             for v in self.video_list]

        # 视频播放区
        player_layout = BoxLayout(size_hint_y=0.4, orientation='vertical')
        player_label = Label(text='视频播放器', size_hint_y=None, height=30,
                           font_name='SimHei')

        self.video_player = VideoPlayer(
            options={'allow_stretch': True},
            state='stop'
        )

        player_layout.add_widget(player_label)
        player_layout.add_widget(self.video_player)

        # 配音控制区
        dub_layout = BoxLayout(size_hint_y=None, height=80, spacing=10, orientation='vertical')

        dub_btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        self.btn_record = Button(text='开始配音', font_name='SimHei')
        self.btn_record.bind(on_press=self.toggle_recording)

        self.btn_play_audio = Button(text='播放配音', font_name='SimHei')
        self.btn_play_audio.bind(on_press=self.play_recorded_audio)

        self.btn_save = Button(text='保存配音', font_name='SimHei')
        self.btn_save.bind(on_press=self.save_dubbed_video)

        dub_btn_layout.add_widget(self.btn_record)
        dub_btn_layout.add_widget(self.btn_play_audio)
        dub_btn_layout.add_widget(self.btn_save)

        self.status_label = Label(text='请选择视频进行配音', size_hint_y=None, height=30,
                                 font_name='SimHei')

        dub_layout.add_widget(dub_btn_layout)
        dub_layout.add_widget(self.status_label)

        # 组装主布局
        root.add_widget(btn_layout)
        root.add_widget(list_label)
        root.add_widget(self.video_rv)
        root.add_widget(player_layout)
        root.add_widget(dub_layout)

        return root

    def add_videos(self, instance):
        """添加视频文件"""
        if HAS_PLYER:
            # 使用 plyer 文件选择器
            filechooser.open_file(
                title='选择视频文件',
                filters=['*.mp4', '*.avi', '*.mov', '*.mkv', '*.3gp', '*.webm'],
                multiple=True,
                on_selection=self.on_file_selected
            )
        else:
            # 桌面端备用：使用弹窗输入路径
            self.show_path_input_popup()

    def show_path_input_popup(self):
        """显示路径输入弹窗（桌面端备用）"""
        from kivy.uix.textinput import TextInput

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text='输入视频文件路径:', font_name='SimHei'))

        path_input = TextInput(multiline=False, size_hint_y=None, height=40)
        content.add_widget(path_input)

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_add = Button(text='添加', font_name='SimHei')
        btn_cancel = Button(text='取消', font_name='SimHei')

        popup = Popup(title='添加视频', content=content, size_hint=(0.9, 0.4))

        def add_path(instance):
            path = path_input.text.strip()
            if path and os.path.exists(path):
                self.add_video_to_list(path)
            popup.dismiss()

        btn_add.bind(on_press=add_path)
        btn_cancel.bind(on_press=popup.dismiss)

        btn_layout.add_widget(btn_add)
        btn_layout.add_widget(btn_cancel)
        content.add_widget(btn_layout)

        popup.open()

    def on_file_selected(self, selection):
        """文件选择回调"""
        if selection:
            for path in selection:
                if isinstance(path, list):
                    for p in path:
                        self.add_video_to_list(p)
                else:
                    self.add_video_to_list(path)

    def add_video_to_list(self, path):
        """添加视频到列表"""
        if os.path.exists(path):
            name = os.path.basename(path)
            self.video_list.append({
                'name': name,
                'path': path,
                'selected': False
            })
            self.update_video_list_view()
            self.save_video_list()
            self.status_label.text = f'已添加: {name}'

    def clear_videos(self, instance):
        """清空视频列表"""
        self.video_list = []
        self.current_video_index = -1
        self.video_player.state = 'stop'
        self.video_player.source = ''
        self.update_video_list_view()
        self.save_video_list()
        self.status_label.text = '列表已清空'

    def update_video_list_view(self):
        """更新视频列表视图"""
        self.video_rv.data = [{'name': v['name'], 'path': v['path'], 'selected': i == self.current_video_index}
                             for i, v in enumerate(self.video_list)]

    def select_video(self, index):
        """选择视频"""
        if 0 <= index < len(self.video_list):
            self.current_video_index = index
            video = self.video_list[index]
            self.video_player.source = video['path']
            self.video_player.state = 'play'
            self.update_video_list_view()
            self.status_label.text = f'正在播放: {video["name"]}'

    def toggle_recording(self, instance):
        """切换录音状态"""
        if self.current_video_index < 0:
            self.status_label.text = '请先选择一个视频!'
            return

        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """开始录音"""
        if HAS_PLYER:
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                self.current_audio_path = os.path.join(
                    self.get_storage_path(),
                    f'dubbing_{timestamp}.wav'
                )
                audio.start_recording(self.current_audio_path)
                self.is_recording = True
                self.btn_record.text = '停止配音'
                self.status_label.text = '正在配音中...'
            except Exception as e:
                self.status_label.text = f'录音失败: {str(e)}'
                Logger.error(f"Recording error: {e}")
        else:
            # 桌面端备用方案：提示用户
            self.status_label.text = '录音功能需要在移动设备上使用'

    def stop_recording(self):
        """停止录音"""
        if HAS_PLYER:
            try:
                audio.stop_recording()
                self.is_recording = False
                self.btn_record.text = '开始配音'
                self.status_label.text = f'配音已保存: {os.path.basename(self.current_audio_path)}'
            except Exception as e:
                self.status_label.text = f'停止录音失败: {str(e)}'
                Logger.error(f"Stop recording error: {e}")

    def play_recorded_audio(self, instance):
        """播放录制的音频"""
        if self.current_audio_path and os.path.exists(self.current_audio_path):
            try:
                sound = SoundLoader.load(self.current_audio_path)
                if sound:
                    sound.play()
                    self.status_label.text = '正在播放配音...'
                else:
                    self.status_label.text = '无法加载音频文件'
            except Exception as e:
                self.status_label.text = f'播放失败: {str(e)}'
        else:
            self.status_label.text = '没有可播放的配音'

    def save_dubbed_video(self, instance):
        """保存配音后的视频（合并视频和音频）"""
        if self.current_video_index < 0:
            self.status_label.text = '请先选择视频!'
            return

        if not self.current_audio_path or not os.path.exists(self.current_audio_path):
            self.status_label.text = '请先录制配音!'
            return

        # 提示用户合并功能
        self.show_merge_popup()

    def show_merge_popup(self):
        """显示合并选项弹窗"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text='视频合并功能需要 FFmpeg 支持。\n'
                 '在 Android 设备上，请安装 FFmpeg 后使用。\n\n'
                 '配音音频已保存在:\n' + self.current_audio_path,
            font_name='SimHei',
            text_size=(400, None),
            halign='center'
        ))

        btn_close = Button(text='关闭', font_name='SimHei', size_hint_y=None, height=50)
        popup = Popup(title='保存配音', content=content, size_hint=(0.9, 0.5))
        btn_close.bind(on_press=popup.dismiss)

        content.add_widget(btn_close)
        popup.open()

    def get_storage_path(self):
        """获取存储路径"""
        if hasattr(self, 'user_data_dir'):
            return self.user_data_dir
        return os.path.expanduser('~')

    def save_video_list(self):
        """保存视频列表到文件"""
        try:
            data_path = os.path.join(self.get_storage_path(), 'video_list.json')
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(self.video_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            Logger.error(f"Save video list error: {e}")

    def load_video_list(self):
        """从文件加载视频列表"""
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