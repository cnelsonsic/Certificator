import os
from weasyprint import HTML
import pyinotify

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        if event.pathname.endswith(".html"):
            print "Creating:", event.pathname

            print "Loading file"
            wprint = HTML(filename=event.pathname)
            print "writing thumbnail"
            wprint.write_png(event.pathname.replace(".html", "_thumbnail.png")+".partial", resolution=10)
            print "writing pdf"
            wprint.write_pdf(event.pathname.replace(".html", ".pdf")+".partial")
            print "writing png"
            wprint.write_png(event.pathname.replace(".html", ".png")+".partial", resolution=300)

            # Remove the ".partial" to indicate that it's done generating both.
            for suffix in ('.pdf', '.png', '_thumbnail.png'):
                dest = event.pathname.replace(".html", suffix)
                src = dest + ".partial"
                os.rename(src, dest)

def main():
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CREATE
    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)
    wdd = wm.add_watch('./generated', mask, rec=True)
    notifier.loop()

if __name__ == "__main__":
    main()
