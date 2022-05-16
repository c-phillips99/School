using System;

using System.Collections.Generic;
using System.Collections.Immutable;
using System.Linq;
using System.Threading;
using System.Threading.Channels;

using System.IO;

using System.Net;
using System.Net.Sockets;
using System.Threading.Tasks;

using System.Web;


namespace Project2
{
    class Program
    {
        // store issue tracker entries
        static ImmutableSortedDictionary<int,Tuple<string, string, string>> issues = new SortedDictionary<int,Tuple<string, string, string>>{{1, new Tuple<string, string, string> ("Project 2", "", "Default")},{2, new Tuple <string, string, string>("This HTML!", "", "Default")}}.ToImmutableSortedDictionary(); 
        static Int32 port;
        const string ip = "127.0.0.1";
        
        static async Task Main(string[] args)
        {
            if (args.Length == 0){
                Console.WriteLine("Please enter a port number.");
                Console.WriteLine("Usage: dotnet run <port>");
                return;
            }
            
            bool test = int.TryParse(args[0], out port);
            if (!test)
            {
                Console.WriteLine("Please enter a port number.");
                Console.WriteLine("Usage: dotnet run <port>");
                return;
            }
            
            IPAddress localAddr = IPAddress.Parse(ip); 
            var server = new TcpListener(localAddr, port);
            // handles concurrent updates to issues dict
            Channel<string> dataChannel = Channel.CreateUnbounded<string>();

            while(true) 
            {
                try 
                {
                    server.Start();
                    Console.WriteLine("Listening for connections... ");
                    
                    // accept connections async
                    TcpClient client = await server.AcceptTcpClientAsync();   
                    string connection = client.Client.RemoteEndPoint.ToString();
                    Console.WriteLine("Connected to "+ connection +"!");
                    
                    /// handle connection async
                    var t = new Thread(() => RunClient(client,dataChannel, connection));
                    t.Start();
                    
                }
                catch (IOException e)
                {
                    Console.WriteLine(e);
                }
                finally
                {                   
                    server.Stop();
                }
                
            }
        }
        
        // handles transmissions on a particular connection async
        static async void RunClient(TcpClient c, Channel<string> channel, string connStr){
            try
            {
                // request fields 
                string method = null;
                string path = "/index.html";
                string version = "HTTP/1.1";
                string host = "localhost:" + port.ToString();
                int contentLength = 0;
                string dataString = "";

                NetworkStream stream = c.GetStream();
                // Receive request
                while (true){
                    using (var sr = new StreamReader(stream))
                    {
                        Task<string> tLine0 = sr.ReadLineAsync();
                        var line0 = tLine0.Result;
                        if (line0 == null) 
                            continue;
                        var vs = line0.Split(" ");
                        if (vs.Length == 3)
                        {
                            method = vs[0];
                            version = vs[2];
                        }
                        while (true)
                        {
                            Task<string> tLine = sr.ReadLineAsync();
                            var line = tLine.Result;
                            if(line.StartsWith("Content-Length:")) contentLength = Convert.ToInt32(line.Split(":")[1].Trim());
                            
                            // read byte data
                            if (String.IsNullOrEmpty(line))
                            {
                                if(sr.Peek() > -1)
                                {
                                    char[] data = new char[contentLength];
                                    Task<int> d = sr.ReadAsync(data,0,contentLength);
                                    dataString = new string(data);
                                }
                                break;
                            }
                        }
                        
                        // Respond
                        using (var sw = new StreamWriter(stream))
                        {
                            string resCode = "200 OK";
                            if (method == "POST")
                            {
                                resCode = "302 Found"; // redirect
                                // put data into channel to update issues dict sequentially
                                ChannelWriter<string> dataChannelWrite = channel.Writer;
                                bool written = dataChannelWrite.TryWrite(dataString);
                                if(written) processPost(channel); 

                            } else if(!File.Exists(Directory.GetCurrentDirectory() + path))
                            {
                                resCode = "404 Not Found";
                            }

                            string html = generateHTML(path);
                            byte[] htmlBytes = System.Text.Encoding.ASCII.GetBytes(html);

                            // response fields
                            string msg = "";
                            string statusLine = version + " " + resCode + "\n"; 
                            string dateLine = "Date: " + DateTime.Now.ToUniversalTime() + "\n";
                            string serverLine = "Server: " + host + "\n";
                            string lastModLine = "Last-Modified: " + File.GetLastWriteTime(path).ToString() + "\n";
                            string contentLengthLine = "Content-Length: " + htmlBytes.Length + "\n";
                            string contentTypeLine = "Content-Type: text/html\n";
                            string connectionLine = "Connection: Closed\n";
                            string emptyLine = "\n";

                            var msgParts = new List<string>();
                            
                            // compose message
                            switch (method)
                            {
                                case "GET":
                                    msgParts = new List<string>{statusLine, dateLine, serverLine, 
                                                        lastModLine, contentLengthLine, contentTypeLine, 
                                                        connectionLine, emptyLine, html};
                                    break;
                                case "POST":
                                    string location = "Location: " + "http://" + host + path + "\n";
                                    msgParts = new List<string>{statusLine, location, dateLine, serverLine, 
                                                                lastModLine, contentLengthLine, contentTypeLine,
                                                                connectionLine, emptyLine, html};
                                    break;
                                case "HEAD":
                                    msgParts = new List<string>{statusLine, dateLine, serverLine, 
                                                        lastModLine, contentLengthLine, contentTypeLine, 
                                                        connectionLine, emptyLine, html};
                                    break;
                                default:
                                    break;
                            }

                            msg = String.Join("", msgParts);
                            await sw.WriteAsync(msg);
                        }
                    }
                    break;
                }
            }
            catch(SocketException e)
            {
                Console.WriteLine("SocketException: {0}", e);
            }
            
        }
        // used to load and update html for displaying issues on page
        static string generateHTML(string reqPath)
        {
            string baseHTML = File.ReadAllText(Directory.GetCurrentDirectory() + reqPath);
            string td = "";

            // present newest table of issue data
            foreach(KeyValuePair<int,Tuple<string, string, string>> kvp in issues)
            {
                string boxCode = "<form action=\"index.html\" method=\"post\">" +  "\n" +
                                    "<select id=\"status\" name=\"status\" onchange=\"this.form.submit()\">" + "\n" +
                                        "<option value=\"Unassigned\">Unassigned</option>" + "\n" +
                                        "<option value=\"Assigned\">Assigned</option>" + "\n" +
                                        "<option value=\"In Progress\">In Progress</option>" + "\n" +
                                        "<option value=\"Complete\">Complete</option>" + "\n" +
                                        "<input type=\"hidden\" id=\"metadata\" name=\"metadata\" value=\"existing\">" + "\n" +
                                        $"<input type=\"hidden\" id=\"key\" name=\"key\" value=\"{kvp.Key.ToString()}\">" + "\n" +
                                        $"<input type=\"hidden\" id=\"issue\" name=\"issue\" value=\"{kvp.Value.Item1}\">" + "\n" +
                                        $"<input type=\"hidden\" id=\"assignee\" name=\"assignee\" value=\"{kvp.Value.Item3}\">" + "\n" +
                                    "</select><br>" + "\n" +
                                "</form>" + "\n";
                string find = "value=\""+ kvp.Value.Item2 + "\"";
                boxCode = boxCode.Replace(find, find + " selected");
                td +=   $"\t<tr>\n" +
                            $"  \t\t<td>{kvp.Key.ToString()}</td>\n" +
                            $"  \t\t<td>{kvp.Value.Item1}</td>\n" +
                            $"  \t\t<td>{boxCode}</td>\n" +
                            $"  \t\t<td>{kvp.Value.Item3}</td>\n" +
                        $"\t</tr>\n";
            }
            string resHTML = baseHTML.Replace("GenerateDataHere!!",td);
            
            return resHTML;
        }

        // update issues dict from post request
        static void processPost(Channel<string> chan)
        {
            //example data: "issue=&status=Unassigned&assignee=John+Doe"
            ChannelReader<string> dataChannelRead = chan.Reader;
            string chanData = "";
            bool read = dataChannelRead.TryRead(out chanData);
            if(read)
            {
                string urlDecoded = HttpUtility.UrlDecode(chanData);
                string[] fields = urlDecoded.Split("&");
                
                // issue entry fields
                int key = -1;
                string issue = "";
                string status = "";
                string assignee = "";
                string metadata = "";
                
                foreach(string field in fields)
                {
                    if (field.StartsWith("key="))
                        key = Convert.ToInt32(field.Substring(field.IndexOf("=") + 1));
                    else if (field.StartsWith("issue="))
                        issue = field.Substring(field.IndexOf("=") + 1);
                    else if (field.StartsWith("status="))
                        status = field.Substring(field.IndexOf("=") + 1);
                    else if (field.StartsWith("assignee="))
                        assignee = field.Substring(field.IndexOf("=") + 1);
                    else if (field.StartsWith("metadata="))
                        metadata = field.Substring(field.IndexOf("=") + 1);
                    else continue;
                }

                if(metadata == "existing")
                {
                    issues = issues.SetItem(key, new Tuple <string, string, string> (issue, status, assignee));
                }
                else if (metadata == "new")
                {
                    key = issues.Keys.Last() + 1;
                    issues = issues.Add(key,new Tuple <string, string, string> (issue, status, assignee));
                }
            }
        }
    }
}
