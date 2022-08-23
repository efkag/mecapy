import keyboard

sin = ""
val = 0.0

def key_pressed(e, *a, **kw):
        global sin, val
        
        # print(e, a, kw)
        k = e.name
        if k in "0123456789":
                sin += k
        elif k == 'enter':
                val += float(sin)/100.0
                print("Entered: " + sin)
                print('Value: ', val)
                sin = ""
keyboard.on_press(key_pressed)