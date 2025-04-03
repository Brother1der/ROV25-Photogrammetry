using System;
using System.Drawing;
using System.IO;
using System.Timers;
using System.Windows.Forms;
using System.Runtime.InteropServices;
using AForge.Video;
using AForge.Video.DirectShow;

class Program
{
    private static MJPEGStream stream;
    private static int frameCount = 0;
    private static bool isCapturing = false;
    private static Timer captureTimer;
    private static readonly string savePath = "captured_frame_{0}.jpg";
    private static int capturedFrames = 0;
    private const int WM_HOTKEY = 0x0312;

    [DllImport("user32.dll")]
    private static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);

    [DllImport("user32.dll")]
    private static extern bool UnregisterHotKey(IntPtr hWnd, int id);

    [STAThread]
    static void Main()
    {
        string cameraUrl = "http//unknown"; // Replace with camera's stream URL
        stream = new MJPEGStream(cameraUrl);
        stream.NewFrame += OnNewFrame;
        stream.Start();
        
        HookKeyboard();
        
        Application.Run(); // Keeps the application running
    }

    private static void OnNewFrame(object sender, NewFrameEventArgs eventArgs)
    {
        if (!isCapturing) return;
        
        frameCount++;
        if (frameCount % 5 == 0) // Captures every 5th frame from camera
        {
            using (Bitmap capturedFrame = (Bitmap)eventArgs.Frame.Clone())
            {
                string filename = string.Format(savePath, capturedFrames++);
                capturedFrame.Save(filename);
            }
        }
    }

    private static void HookKeyboard()
    {
        RegisterHotKey(IntPtr.Zero, 1, (uint)(0x0001 | 0x0004), (uint)Keys.I); // Alt + Shift + I
        Application.AddMessageFilter(new HotKeyMessageFilter());
    }

    private class HotKeyMessageFilter : IMessageFilter
    {
        public bool PreFilterMessage(ref Message m)
        {
            if (m.Msg == WM_HOTKEY)
            {
                StartCapturing();
                return true;
            }
            return false;
        }
    }

    private static void StartCapturing()
    {
        if (isCapturing) return;
        
        isCapturing = true;
        frameCount = 0;
        capturedFrames = 0;
        
        captureTimer = new Timer(60000); // 1 minute
        captureTimer.Elapsed += (sender, e) => StopCapturing();
        captureTimer.AutoReset = false;
        captureTimer.Start();
    }

    private static void StopCapturing()
    {
        isCapturing = false;
        captureTimer?.Dispose();
        MessageBox.Show("Frame capture stopped after 1 minute.", "Capture Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);
    }
}
//need to add a script that runs the bat file that i will make later.