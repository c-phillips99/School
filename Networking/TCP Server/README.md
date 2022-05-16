# TCP Webserver

A static issue tracker HTTP webserver written in TCP to handle the concurrency of multiple clients. This was one of three networking class projects aimed at understanding UPD, TCP, and HTTP protocols and their unique strengths and weaknesses. 

## Getting Started

To run the webserver, use "dotnet run \<port\>" at the root directory of this project in a command prompt. Then visit "localhost:\<port\>" in Google Chrome.

### Prerequisites

This project was built using .NET Core SDK version 3.1.1 for Windows x64 and designed to work with Google Chrome.

### Installing

To get .Net Core version 3.1.1 SDK:

1. Visit <https://dotnet.microsoft.com/download> and select "Download .Net Core SDK"

![Download Instr](readme_files/DownloadNetCore.PNG)

* If you plan to use .NET Core 3.1 with Visual Studio, then VS version 2019 16.4 or newer is required.

2. After following the install instructions, confirm that the installation was successful and check what version you are using by opening a Windows command prompt and entering the following:
```
$>dotnet --version
3.1.101
```
Our version number is 3.1.101 as seen above.
## Acknowledgments

* Dr. Ryan Yates was the professor of this networking class and project
* Contributors: Colten Phillips, Ryan Nickelsen, and Ryan Ozzello

