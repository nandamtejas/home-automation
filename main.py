from kivymd.app import MDApp
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.taptargetview import MDTapTargetView
from kivymd.uix.list import OneLineListItem, IRightBodyTouch,TwoLineAvatarListItem
from kivymd.uix.selectioncontrol import MDSwitch
from android.permissions import request_permissions,Permission
from android.runnable import run_on_ui_thread
from jnius import autoclass
from plyer import stt,notification
from functools import partial


# for permissions https://developer.android.com/reference/android/Manifest.permission
kv = '''
<IconTooltipButton@MDFloatingActionButton+MDTooltip>

ScreenManager: 
    Main:


<Main>:
    name: "Main"
    BoxLayout:
        orientation:'vertical'

        MDToolbar:
            title: 'Home Automation'
            specific_text_color: 1,1,1,1
            halign: "center"
            elevation: 100
            right_action_items: [['bluetooth-connect', lambda x: app.ss()],['bluetooth-off', lambda x: app.ble.BluetoothAdapter().getDefaultAdapter().disable()]]

        MDBottomNavigation:
            id: navigation 
            panel_color: 1,1,1,1
            text_color_active: 0,0,0,1
                

            MDBottomNavigationItem:
                id: speech_id
                name: 'screen speech'
                text: 'Speech'
                icon: 'voice'
                    

                IconTooltipButton:
                    id: speech
                    icon: 'microphone'
                    md_bg_color: app.theme_cls.primary_light
                    tooltip_text: self.icon + " input" 
                    user_font_size: '64sp'
                    pos_hint: {'center_x':0.5,'center_y':0.5}
                    on_release: root.tap_target_start()


            MDBottomNavigationItem:
                id: switch_id
                name: 'screen switch'
                text: 'Switch'
                icon: 'toggle-switch'
                ScrollView:
                    MDList:
                        id: lists

<ListItemWithSwitch>:
    text: ''
    pos_hint:{'center_x':0.8,'center_y':0.5}
    RightSwitch:
        id: root.text
        pos_hint:{'center_x':0.9,'center_y':0.5}
        on_active: app.check_send(root.text,*args)


<Item>:
    IconLeftWidget:
        icon: root.source
'''

class AndroidBluetoothClass:
    
    def getAndroidBluetoothSocket(self,DeviceName):
        self.paired_devices = self.BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        socket = None
        for device in self.paired_devices:
            if device.getName() == DeviceName:
                socket = device.createRfcommSocketToServiceRecord(
                    self.UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                self.ReceiveData = self.BufferReader(self.InputStream(socket.getInputStream()))
                self.SendData = socket.getOutputStream()
                k = {'buttons':[],'Items':[],'size_hint':(0.5,0.5)}
                try:
                    socket.connect()
                except Exception as e:
                    notification.notify(title="BLUETOOTH",message="Bluetooth Connection Failed")
                    app.open_dialogbox(title="Bluetooth Connection", text="Bluetooth Connection Failed",kwargs=k)
                    return self.ConnectionEstablished
                self.ConnectionEstablished = True
                notification.notify(title="BLUETOOTH",message="Bluetooth Connection Successful")
                app.open_dialogbox(title="Bluetooth Connection", text="Bluetooth Connection Successful",kwargs=k)
                print('Bluetooth Connection successful')
        return self.ConnectionEstablished


    def BluetoothSend(self, Message, *args):
        try:
            if self.ConnectionEstablished == True:
                self.SendData.write(Message)
                self.SendData.flush()
            else:
                notification.notify(title="BLUETOOTH",message="Bluetooth device not connected")
                app.open_dialogbox(title="Bluetooth Error", text="Bluetooth device Not connected",kwargs={'buttons':[],'Items':[],'size_hint':(0.8,0.8)})
        except Exception as e:
            print(str(e))
            if args:
                print(args[0])
                self.getAndroidBluetoothSocket(args[0])


    def BluetoothReceive(self,*args):
        DataStream = ''
        if self.ConnectionEstablished == True:
            DataStream = str(self.ReceiveData.readline())
        return DataStream

    def EnableBluetooth(self):
        if not self.BluetoothAdapter().getDefaultAdapter().isEnabled():
            self.BluetoothAdapter().getDefaultAdapter().enable()
    
    def DisableBluetooth(self):
        self.BluetoothAdapter().getDefaultAdapter().disable()

    def getAllPairedDevices(self):
        if not self.BluetoothAdapter().getDefaultAdapter().isEnabled():
            self.EnableBluetooth()
        return [{'Name':device.getName(),'Address':device.getAddress()} for device in self.paired_devices]


    def __init__(self):
        self.BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        self.BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
        self.BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
        self.UUID = autoclass('java.util.UUID')
        self.BufferReader = autoclass('java.io.BufferedReader')
        self.InputStream = autoclass('java.io.InputStreamReader')
        self.ConnectionEstablished = False
        self.paired_devices = self.BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()


    def __del__(self):
        print('class AndroidBluetooth destroyer')


class ListItemWithSwitch(OneLineListItem):
    pass

class RightSwitch(IRightBodyTouch,MDSwitch):
    pass
        
class Item(TwoLineAvatarListItem):
    source = StringProperty()

class Main(Screen):

    def tap_target_start(self):
        app.builder.get_screen("Main").ids.speech.md_bg_color = app.theme_cls.primary_light
        
        if app.tap_target_view.state == "close":
            app.tap_target_view.start()
            app.tap_target_view.on_open(self.listen_speech())
        else:
            app.tap_target_view.stop()
            app.tap_target_view.on_close(self.stop_listening())            

    def listen_speech(self):
        if stt.listening:
            self.stop_listening()
            return

        a = "Listening"
        b = "Recognizing"

        self.results_text = ''
        self.partial_text = ''
        try:
            stt.start()
            app.tap_target_view.title_text = a
            Clock.schedule_interval(self.check_state, 1 / 5)
        except NotImplementedError:
            pass

    def stop_listening(self):
        a = "Listening"
        b = "Recognizing"

        try:
            stt.stop()
            self.update()
            Clock.unschedule(self.check_state)
        except NotImplementedError:
            pass

    def check_state(self, dt):
        # if the recognizer service stops, change UI
        if not stt.listening:
            self.stop_listening()

    def update(self):
        app.builder.get_screen("Main").ids.speech.md_bg_color = app.theme_cls.primary_light
        if app.tap_target_view.state != 'close':
            app.tap_target_view.stop()
        self.partial_text = '\n'.join(stt.partial_results)
        self.results_text = '\n'.join(stt.results) 
        see = self.results_text.lower()
        app.send_data(message=bytes(see.encode('utf-8')))

sm = ScreenManager()
sm.add_widget(Main(name="Main"))

class TestApp(MDApp):

    def build(self):
        self.ble = AndroidBluetoothClass()
        self.builder = Builder.load_string(kv)
        self.tap_target_view = MDTapTargetView(
            widget = self.builder.get_screen("Main").ids.speech,
            title_text = "This is demo",
            title_text_size = "25dp",
            title_position = "bottom",
            description_text = " ",
            widget_position = "center",
            target_radius = '60dp',
            outer_circle_color = (0.1,0.5,1),
            draw_shadow = True
        )
        for t in ["RED","GREEN","BLUE"]:
           self.builder.get_screen("Main").ids.lists.add_widget(ListItemWithSwitch(text=t))
        return self.builder

    def check_send(self,msg,checkbox,value):
        text = None
        if msg == "RED":
            text = b"red"
        elif msg == "GREEN":
            text = b"green"
        elif msg == "BLUE":
            text = b"blue"
        if value:
            self.send_data(message=text)
        else:
            self.send_data(message=text + b" off")

        if text is None:
            self.send_data(message=b"all off")


    @run_on_ui_thread
    def send_data(self,message:bytes):
        self.ble.BluetoothSend(message,self.device)
        
    
    def open_dialogbox(self,title,text,**kwargs):
        ok_btn = MDFlatButton(text = "Ok", text_color = self.theme_cls.primary_color,on_release=self.close_dialog)
        if kwargs['kwargs']['buttons'] == []:
            buttons = [ok_btn]
        else:
            buttons = kwargs['kwargs']['buttons']
        if kwargs['kwargs']['Items'] != []:
            self.dialog = MDDialog(title = title,text=text,type='confirmation', items=kwargs['kwargs']['Items'], buttons = buttons, size_hint = kwargs['kwargs']['size_hint'])
            self.dialog.open()
        else:
            self.dialog = MDDialog(title = title,text=text, buttons = buttons, size_hint = (0.65,0.55))
            self.dialog.open()

    
    def close_dialog(self,instance):
        self.dialog.dismiss()
    
    
    def ss(self):   
        items = [Item(
            text = device.getName(),
            secondary_text = device.getAddress(),
            source = 'bluetooth-connect',
            on_release = self.connect) for device in self.ble.paired_devices]
        ok_btn = MDRaisedButton(text = "OK", text_color = self.theme_cls.primary_color,on_release=self.close_dialog)
        self.open_dialogbox(title="Paired Devices", text="Paired Devices",kwargs={'buttons':[ok_btn],'Items':items,'size_hint':(0.8,0.8)})
    
    
    def connect(self,instance):
        self.close_dialog(instance)
        self.device = instance.text
        self.ble.getAndroidBluetoothSocket(instance.text)
        

    def on_start(self): 
        request_permissions([Permission.RECORD_AUDIO,Permission.BLUETOOTH,Permission.BLUETOOTH_ADMIN,Permission.ACCESS_FINE_LOCATION])
        #self.ble.BluetoothAdapter().getDefaultAdapter().enable()
    
    def on_pause(self):
        return True

app = TestApp()
app.run()