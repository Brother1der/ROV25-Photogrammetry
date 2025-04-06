using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;
using AForge.Video;

class Program
{
    private static MJPEGStream stream;
    private static int frameCount = 0;
    private static bool isCapturing = false;
    private static System.Timers.Timer captureTimer;
    private static readonly string outputDir = "CapturedFrames";
    private static readonly string savePath = Path.Combine(outputDir, "captured_frame_{0}.jpg");
    private static int capturedFrames = 0;
    private const int WM_HOTKEY = 0x0312;
    private static readonly string batchFilePath = @"C:\Path\To\LaunchSilent.vbs"; // Use VBS for silent execution
    private static bool isRunning = true;

    [DllImport("user32.dll")]
    private static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);

    [DllImport("user32.dll")]
    private static extern bool UnregisterHotKey(IntPtr hWnd, int id);

    [DllImport("user32.dll")]
    private static extern bool PeekMessage(out MSG lpMsg, IntPtr hWnd, uint wMsgFilterMin, uint wMsgFilterMax, uint wRemoveMsg);

    [StructLayout(LayoutKind.Sequential)]
    public struct MSG
    {
        public IntPtr hwnd;
        public uint message;
        public IntPtr wParam;
        public IntPtr lParam;
        public uint time;
        public System.Drawing.Point pt;
    }

    static void Main()
    {
        Directory.CreateDirectory(outputDir);

        string cameraUrl = "http://your_camera_ip/mjpeg"; // Replace with actual stream URL
        stream = new MJPEGStream(cameraUrl);
        stream.NewFrame += OnNewFrame;
        stream.Start();

        // Register Alt+Shift+I to start capture
        RegisterHotKey(IntPtr.Zero, 1, 0x0001 | 0x0004, (uint)ConsoleKey.I);

        // Register Alt+Shift+O to stop program
        RegisterHotKey(IntPtr.Zero, 2, 0x0001 | 0x0004, (uint)ConsoleKey.O);

        Console.WriteLine("Running. Press Alt + Shift + I to capture. Alt + Shift + O to exit.");

        while (isRunning)
        {
            if (PeekMessage(out MSG msg, IntPtr.Zero, 0, 0, 1))
            {
                if (msg.message == WM_HOTKEY)
                {
                    int hotkeyId = msg.wParam.ToInt32();
                    if (hotkeyId == 1)
                        StartCapturing();
                    else if (hotkeyId == 2)
                        StopProgram();
                }
            }

            Thread.Sleep(10);
        }

        Cleanup();
    }

    private static void OnNewFrame(object sender, NewFrameEventArgs eventArgs)
    {
        if (!isCapturing) return;

        frameCount++;
        if (frameCount % 5 == 0)
        {
            using (Bitmap capturedFrame = (Bitmap)eventArgs.Frame.Clone())
            {
                string filename = string.Format(savePath, capturedFrames++);
                capturedFrame.Save(filename);
            }
        }
    }

    private static void StartCapturing()
    {
        if (isCapturing) return;

        isCapturing = true;
        frameCount = 0;
        capturedFrames = 0;

        captureTimer = new System.Timers.Timer(10000); // 10 seconds
        captureTimer.Elapsed += (sender, e) => StopCapturing();
        captureTimer.AutoReset = false;
        captureTimer.Start();
    }

    private static void StopCapturing()
    {
        isCapturing = false;
        captureTimer?.Dispose();
        RunBatchFile();
    }

    private static void StopProgram()
    {
        isRunning = false;
    }

    private static void RunBatchFile()
    {
        try
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = batchFilePath,
                UseShellExecute = true,
                CreateNoWindow = true
            });
        }
        catch (Exception)
        {
            // Optionally log to a file
        }
    }

    private static void Cleanup()
    {
        if (stream.IsRunning)
            stream.SignalToStop();

        UnregisterHotKey(IntPtr.Zero, 1);
        UnregisterHotKey(IntPtr.Zero, 2);
    }
}