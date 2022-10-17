import speedify

show_functions = [
    speedify.show_servers,
    speedify.show_settings,
    speedify.show_privacy,
    speedify.show_adapters,
    speedify.show_currentserver,
    speedify.show_user,
    speedify.show_directory,
    speedify.show_connectmethod,
    speedify.show_streamingbypass,
    speedify.show_disconnect,
    speedify.show_streaming,
    speedify.show_speedtest,
]
for f in show_functions:
    print(f())
