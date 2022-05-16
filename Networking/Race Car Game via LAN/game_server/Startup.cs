using System;
using System.Threading;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.FileProviders;
using Microsoft.AspNetCore.StaticFiles;
using System.IO;
using Microsoft.Extensions.FileProviders.Physical;
using Microsoft.AspNetCore.Routing;
using System.Net.WebSockets;
using Microsoft.AspNetCore.Authentication.Certificate;
using System.Text.Json;

namespace project3
{
    public class Startup
    {
        // Open connections
        Dictionary<string,WebSocket> conns = new Dictionary<string, WebSocket>();
        // Server state view
        Dictionary<string,Dictionary<string,object>> local_states = new Dictionary<string, Dictionary<string,object>>();
        Dictionary<string,object> global_state = new Dictionary<string, object>();

        public void ConfigureServices(IServiceCollection services)
        {
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }

            // Serves rocket.html
            app.UseStaticFiles();
            app.UseStaticFiles(new StaticFileOptions()
            {
                FileProvider = new PhysicalFileProvider(Path.Combine(Directory.GetCurrentDirectory(), @"default"))
            });

            app.UseWebSockets();
            app.Use(async (context, next) =>
            {
                if (context.Request.Path == "/step")
                {
                    if (context.WebSockets.IsWebSocketRequest)
                    {
                        try
                        {
                            // Make connection
                            WebSocket webSocket = await context.WebSockets.AcceptWebSocketAsync();
                            // Add connection to server list of connections
                            string connStr = context.Connection.RemoteIpAddress.ToString() + ":" + context.Connection.RemotePort.ToString();
                            conns.Add(connStr,webSocket);

                            await Respond(context, webSocket, connStr);
                        } 
                        catch (WebSocketException ex)
                        {
                            switch (ex.WebSocketErrorCode)
                            {
                                case WebSocketError.ConnectionClosedPrematurely:
                                // handle error
                                Console.WriteLine("ConnectionClosedPrematurely");
                                break;
                                default:
                                // handle error
                                Console.WriteLine("Exception Occured");
                                break;
                            }
                        }
                    }
                    else
                    {
                        context.Response.StatusCode = 400;
                    }
                }
                else
                {
                    await next();
                }

            });
        }

        private async Task Respond(HttpContext context, WebSocket webSocket, string conn_str)
        {
            bool global_changed = false;
            if(global_state.Count > 0)
            {
                string json_back = back2JSON("",local_states, global_state);
                byte[] json_bytes = System.Text.Encoding.ASCII.GetBytes(json_back);
                await webSocket.SendAsync(new ArraySegment<byte>(json_bytes, 0, json_bytes.Length), WebSocketMessageType.Text,true, CancellationToken.None);
            }

            // Receive request
            var buffer = new byte[1024 * 4];
            WebSocketReceiveResult result = await webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
            
            while (!result.CloseStatus.HasValue)
            {

                // Read json
                string json_str = System.Text.ASCIIEncoding.ASCII.GetString(buffer.Take(result.Count).ToArray());

                // Parse and collect local/global data form json
                var data = parseJSON(json_str);
                var local = data.Item1; 
                var global = data.Item2;

                // Update server local states
                lock (local_states) // Potential problem?
                {
                    local_states[conn_str] = local;
                }

                // Update server global states
                if(global != null)
                {
                    global_changed = true;
                    lock(global_state) // Also weird
                    {
                        global_state = global;
                    }
                }

                // Send
                
                foreach(string conn in conns.Keys)
                {
                    if(conn_str != conn)
                    {
                        string json_back = "";
                        if(global_changed)
                        {
                            json_back = back2JSON(conn,local_states, global_state);
                        }
                        else
                        {
                            json_back = back2JSON(conn,local_states, null);
                        }
                        // Console.WriteLine(local_states.Keys.Count);
                        // Console.WriteLine(json_back);
                        byte[] json_bytes = System.Text.Encoding.ASCII.GetBytes(json_back);
                        await conns[conn].SendAsync(new ArraySegment<byte>(json_bytes, 0, json_bytes.Length), WebSocketMessageType.Text,true, CancellationToken.None);
                    }
                    
                }

                
                
                global_changed = false;
                // await webSocket.SendAsync(new ArraySegment<byte>(buffer, 0, result.Count), WebSocketMessageType.Text,true, CancellationToken.None);
                result = await webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
            }

            // Remove connection for server list of connections
            conns.Remove(conn_str);
            local_states.Remove(conn_str);
            await webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure,"Data Sent",CancellationToken.None);
            Console.WriteLine("closed");
        }
        
        private static (Dictionary<string,object>,Dictionary<string,object>) parseJSON(string json_str)
        {
            var json = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(json_str);
            List<Dictionary<string,object>> local1 = JsonSerializer.Deserialize<List<Dictionary<string,object>>>(json["local"].GetRawText());
            Dictionary<string,object> local2 = local1[0];

            Dictionary<string,object> global = null;
            if(json.ContainsKey("global"))
            {
                global = JsonSerializer.Deserialize<Dictionary<string, object>>(json["global"].GetRawText());
            }
            
            return (local2, global);
        }

        private static string back2JSON(string client_conn_str, Dictionary<string,Dictionary<string,object>> server_locals, Dictionary<string,object> server_globals)
        {
            string json_global = "";
            string json_local = "";
            string json = "";

            // locals
            Dictionary<string,Dictionary<string,object>> server_locals_copy = new Dictionary<string, Dictionary<string, object>>(server_locals); 
            // Don't send client locals data to them
            server_locals_copy.Remove(client_conn_str);
            // Remove conn_str identifiers
            List<Dictionary<string,object>> values_locals = server_locals_copy.Values.ToList();
            json_local = JsonSerializer.Serialize(values_locals);

            // global
            if(server_globals != null)
            {
                Dictionary<string,object> server_globals_copy = new Dictionary<string, object>(server_globals);
                json_global = JsonSerializer.Serialize(server_globals_copy);
                json += "\"global\":" + json_global +",";       
            }

            // Final json to send back
            json = "{" + 
                json + "\"local\":" + json_local + 
                    "}";

            return json;
        }

        public static string ToDebugString<TKey, TValue> (IDictionary<TKey, TValue> dictionary)
        {
            return "{" + string.Join(",", dictionary.Select(kv => kv.Key + "=" + kv.Value).ToArray()) + "}";
        }
        


    }
}
