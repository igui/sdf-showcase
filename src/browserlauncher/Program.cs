using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;

namespace BrowserLauncher
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            System.Diagnostics.Process proc = new System.Diagnostics.Process();
            proc.EnableRaisingEvents = false;
            string dir = System.IO.Directory.GetCurrentDirectory();
            proc.StartInfo.FileName = dir + "\\_browser.bat";
            proc.StartInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
            proc.Start();
        }
    }
}
