using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Threading;
using System.IO.Compression;

namespace RiskShieldLauncher
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.Title = "RiskShield AI Manager Setup";
            Console.WriteLine("===================================================");
            Console.WriteLine("       RiskShield AI Manager - Auto Installer      ");
            Console.WriteLine("===================================================");
            Console.WriteLine();
            
            string appDir = AppDomain.CurrentDomain.BaseDirectory;
            
            // Step 1: Check Python
            Console.WriteLine("[1/5] Checking Python installation...");
            if (!IsCommandAvailable("python --version"))
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("ERROR: Python is not installed or not in PATH.");
                Console.WriteLine("Please install Python 3.10+ from python.org and ensure 'Add to PATH' is checked.");
                Console.ResetColor();
                Console.WriteLine("Press any key to exit...");
                Console.ReadKey();
                return;
            }
            
            // Step 2: Check Node.js
            Console.WriteLine("[2/5] Checking Node.js installation...");
            if (!IsCommandAvailable("npm --version"))
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("ERROR: Node.js/npm is not installed or not in PATH.");
                Console.WriteLine("Please install Node.js from nodejs.org.");
                Console.ResetColor();
                Console.WriteLine("Press any key to exit...");
                Console.ReadKey();
                return;
            }
            
            // Step 3: Check/Run Backend Installation
            Console.WriteLine("[3/5] Checking backend dependencies...");
            string backendDir = Path.Combine(appDir, "backend");
            if (!Directory.Exists(Path.Combine(backendDir, ".venv")))
            {
                Console.WriteLine("      Setting up Python virtual environment (this may take a few minutes)...");
                RunCommand("cmd.exe", "/c \"python -m venv .venv && call .venv\\Scripts\\activate.bat && pip install -r requirements.txt\"", backendDir);
                Console.WriteLine("      Backend setup complete.");
            }
            else
            {
                Console.WriteLine("      Backend already configured.");
            }

            // Step 4: Check/Run Frontend Installation
            Console.WriteLine("[4/5] Checking frontend dependencies...");
            string frontendDir = Path.Combine(appDir, "frontend");
            if (!Directory.Exists(Path.Combine(frontendDir, "node_modules")))
            {
                Console.WriteLine("      Installing Node modules (this may take a few minutes)...");
                RunCommand("cmd.exe", "/c \"npm install\"", frontendDir);
                Console.WriteLine("      Frontend setup complete.");
            }
            else
            {
                Console.WriteLine("      Frontend already configured.");
            }
            
            // Step 5: Optional AI Copilot Setup
            Console.WriteLine("[5/5] Checking optional AI Copilot (Ollama/Zephyr)...");
            if (IsCommandAvailable("ollama --version"))
            {
                Console.WriteLine("      Ollama detected. Ensuring service is running...");
                // Start ollama serve in background quietly
                Process process = new Process();
                process.StartInfo.FileName = "cmd.exe";
                process.StartInfo.Arguments = "/c start /b ollama serve >nul 2>nul";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.CreateNoWindow = true;
                process.Start();
                
                Thread.Sleep(2000); // Wait for service to warm up

                Console.WriteLine("      Pulling zephyr:7b-beta model if missing (may take time on first run)...");
                RunCommand("cmd.exe", "/c \"ollama pull zephyr:7b-beta\"", appDir);
                Console.WriteLine("      AI Copilot ready.");
            }
            else
            {
                Console.ForegroundColor = ConsoleColor.DarkGray;
                Console.WriteLine("      Ollama not detected. Skipping Copilot setup.");
                Console.WriteLine("      (To enable the AI Copilot, install Ollama from https://ollama.ai)");
                Console.ResetColor();
            }

            Console.WriteLine();
            Console.WriteLine("===================================================");
            Console.WriteLine("Setup Complete! Starting RiskShield AI Manager...");
            Console.WriteLine("===================================================");
            Thread.Sleep(1500);
            
            // Launch the start_app.bat script
            string startScript = Path.Combine(appDir, "start_app.bat");
            if (File.Exists(startScript))
            {
                Process process = new Process();
                process.StartInfo.FileName = "cmd.exe";
                process.StartInfo.Arguments = "/c start_app.bat";
                process.StartInfo.WorkingDirectory = appDir;
                process.StartInfo.UseShellExecute = true;
                process.Start();
            }
            else
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("ERROR: start_app.bat not found in the current directory.");
                Console.ResetColor();
                Console.WriteLine("Press any key to exit...");
                Console.ReadKey();
            }
        }
        
        static bool IsCommandAvailable(string command)
        {
            try
            {
                Process process = new Process();
                process.StartInfo.FileName = "cmd.exe";
                process.StartInfo.Arguments = "/c " + command;
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;
                process.Start();
                process.WaitForExit();
                return process.ExitCode == 0;
            }
            catch
            {
                return false;
            }
        }
        
        static void RunCommand(string filename, string arguments, string workingDirectory)
        {
            Process process = new Process();
            process.StartInfo.FileName = filename;
            process.StartInfo.Arguments = arguments;
            process.StartInfo.WorkingDirectory = workingDirectory;
            process.StartInfo.UseShellExecute = false;
            process.Start();
            process.WaitForExit();
        }
    }
}
