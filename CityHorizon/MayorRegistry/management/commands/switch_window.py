from django.core.management.base import BaseCommand
import win32gui
import win32con
import win32api
import win32process
import time


class Command(BaseCommand):
    help = 'Cycle through non-File Explorer windows'

    def handle(self, *args, **options):
        try:
            while True:
                hwnd = win32gui.GetForegroundWindow()
                current_pid = win32process.GetWindowThreadProcessId(hwnd)[1]

                found = False
                while True:
                    next_hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)
                    if next_hwnd == 0:
                        break
                    if win32gui.IsWindowVisible(next_hwnd):
                        class_name = win32gui.GetClassName(next_hwnd)
                        if class_name != "CabinetWClass":
                            pid = win32process.GetWindowThreadProcessId(next_hwnd)[1]
                            if pid != current_pid:
                                win32gui.SetForegroundWindow(next_hwnd)
                                window_title = win32gui.GetWindowText(next_hwnd)
                                self.stdout.write(self.style.SUCCESS(f'Switched to window: {window_title}'))
                                found = True
                                break
                    hwnd = next_hwnd

                if not found:
                    self.stdout.write(self.style.WARNING('No more suitable windows found.'))
                    return

        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Stopped cycling windows.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))