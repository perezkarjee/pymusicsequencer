using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Net.Sockets;
using System.Net;
using System.Text;
using System;
using SimpleJSON;
using JSONConConverter;



public class Client: MonoBehaviour {
    struct TestStruct
    {
        public string name;
        public int level;
        public TestStruct(string name, int level)
        {
            this.name = name;
            this.level = level;
        }
    };

    private UILabel guiConsole;
    private Socket sock = null;
    private byte[] recvBuffer = new byte[10000];
    private byte[] recvedBuffer = new byte[10000];
    int recvedIdx = 0;
    private string host = "127.0.0.1";
    private int port = 54321;
    private List<string> ConsoleTxts = new List<string>();
    private AudioClip bgm;

    // Use this for initialization
    void Start () {
        guiConsole = (UILabel)(GameObject.Find("Console").GetComponent<UILabel>());

        sock = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp );           

        sock.Connect( host, port );
        if( sock.Connected )
        {
            ConsoleMessage( "Connected" );

            // 소켓은 Async로 ReceiveComplete라는 함수가 받기 완료시 불림
            sock.BeginReceive( 
                    recvBuffer,
                    0,
                    recvBuffer.Length,
                    SocketFlags.None,
                    new AsyncCallback( ReceiveComplete ),
                    null );
        }
        else
        {
            ConsoleMessage( "Fail to connect" );
        }             


    }      
    public KeyValuePair<string, JSONCon> KV(string key, int val)
    {
        return new KeyValuePair<string, JSONCon>(key, Int(val));
    }
    public KeyValuePair<string, JSONCon> KV(string key, string val)
    {
        return new KeyValuePair<string, JSONCon>(key, Str(val));
    }
    public KeyValuePair<string, JSONCon> KV(string key, float val)
    {
        return new KeyValuePair<string, JSONCon>(key, Float(val));
    }
    public KeyValuePair<string, JSONCon> KV(string key, JSONCon val)
    {
        return new KeyValuePair<string, JSONCon>(key, val);
    }
    public void Test1() // 걍 텍스트 에코 테스트
    {
        JSONCon dict = Dict(
                KV("msgtype", "txt"),
                KV("txt", "텍스트"),
                KV("testList", List(1, 2, 3, 4.4f, "asd"))
        );
        Send(dict);
    }
    public void Test2()
    {
        JSONCon dict = Dict(
                KV("msgtype", "login"),
                KV("acc", "아이디"),
                KV("pw", "비번")
        );
        Send(dict);

        TestStruct ts = new TestStruct("이름", 10);

        JSONCon dict2 = Dict(
            KV("msgtype", "txtpluslevel"),
            KV("txt", Str(ts.name)),
            KV("level", ts.level)
        );
        Send(dict2);
    }
    public void SendHandshake()
    {
        string hsMsg = "THEPGAMERPG";
        JSONCon dict = Dict(
                KV("msgtype", "handshake"),
                KV("hs", hsMsg)
        );
        Send(dict);
    }

    string Conv(JSONCon data)
    {
        return JSONCon.ConvertToJSON(data);
    }
    JSONCon Dict(params KeyValuePair<string, JSONCon>[] items)
    {
        return JSONCon.GetDict(items);
    }
    JSONCon List(params object[] items)
    {
        JSONCon[] newItems = new JSONCon[items.Length];
        int idx=0;
        foreach(object item in items)
        {
            Type t = item.GetType();
            if(t == typeof(int))
                newItems[idx] = Int((int)item);
            else if(t == typeof(float))
                newItems[idx] = Float((float)item);
            else if(t == typeof(string))
                newItems[idx] = Str((string)item);
            idx += 1;
        }
        return JSONCon.GetList(newItems);
    }
    JSONCon Float(float val)
    {
        return JSONCon.GetFloat(val);
    }
    JSONCon Int(int val)
    {
        return JSONCon.GetInt(val);
    }
    JSONCon Str(string val)
    {
        return JSONCon.GetString(val);
    }
    byte[] GetPacket(string dataStr)
    {
        byte[] txt = Encoding.UTF8.GetBytes(dataStr);
        byte[] packet = new byte[txt.Length+6];
        Buffer.BlockCopy(txt, 0, packet, 0, txt.Length);
        SetTerminator(packet);
        return packet;
    }
    void SetTerminator(byte[] packet)
    {
        int pos = packet.Length-6;
        packet[pos+0] = 127;
        packet[pos+1] = 64;
        packet[pos+2] = 127;
        packet[pos+3] = 64;
        packet[pos+4] = 127;
        packet[pos+5] = 64;
    }

    // Update is called once per frame
    void Update () {

    }

    public void Send(JSONCon data) // byte 배열을 서버로 전송함
    {
        byte[] buffer = GetPacket(Conv(data));
        if( sock != null )
        {
            try
            {                                    
                sock.BeginSend(
                        buffer,
                        0,
                        buffer.Length,
                        SocketFlags.None,
                        new AsyncCallback( SendComplete),
                        null );

            }
            catch( Exception e )
            {
                string tmp = "Exception: " + e.Message;
                ConsoleMessage( "Send Fail:" + tmp );

                Shutdown();
            }
        }
    }

    void OnApplicationQuit()
    {
        Shutdown();
    }

    private void ReceiveComplete( IAsyncResult ar ) // 받기 완료시 불리는 이벤트
    {
        try
        {
            if( null == sock )
                return;

            int len = sock.EndReceive( ar );

            if( len == 0 )
            {
                Shutdown();
            }
            else
            {
                //ConsoleMessage(String.Format("{0} received", recvBuffer[0] ) );
                Buffer.BlockCopy(recvBuffer, 0, recvedBuffer, recvedIdx, len);
                recvedIdx += len;
                sock.BeginReceive(
                        recvBuffer,
                        0,
                        recvBuffer.Length,
                        SocketFlags.None,
                        new AsyncCallback( ReceiveComplete ),
                        null );

                ProcessReceived(); // 받은 걸 처리
            }                     
        }
        catch( Exception e )
        {
            ConsoleMessage( "Exception: " + e.Message );
            Shutdown();
        }
    }      
    private void ProcessReceived()
    {
        byte[] pattern = {127,64,127,64,127,64}; // 패킷의 Footer 

        List<int> foundIdxes = findOccurences(recvedBuffer, pattern);
        int foundIdx = -1;
        if (foundIdxes.Count != 0)
            foundIdx = foundIdxes[0];

        
        if(foundIdx > 0)
        {
             byte[] line = new byte[foundIdx];
             Buffer.BlockCopy(recvedBuffer, 0, line, 0, foundIdx); 
             recvedIdx -= foundIdx+6;
             Buffer.BlockCopy(recvedBuffer, foundIdx+6, recvedBuffer, 0, recvedIdx); 
             ProcessLine(line);
        }
    }
    private void ProcessLine(byte[] line) // 한 종류의 패킷을 처리함
    {
        try
        {
            // 보통 서버는 제대로 된 메시지를 보내므로 굳이 확인할 필요는 없다능...
            
            //ConsoleMessage(Encoding.UTF8.GetString(line));
            var n = JSON.Parse(Encoding.UTF8.GetString(line));
            //ConsoleMessage(n["msgtype"] + ", " + n["txt"]);
            ConsoleMessage(n["msgtype"]);
            string msgT = n["msgtype"]; // 주의: 이걸 string msgT에다 저장하지 않고 if(n["msgtype"] == "txt")로 할 경우 데이터 타입이 달라 제대로 안 됨
            if(msgT == "txt")
            {
                ConsoleMessage(n["txt"]);
                ConsoleMessage(n["test"].Count.ToString());
            }
            else if(msgT == "txtpluslevel")
            {
                ConsoleMessage(n["txt"] + ", " + n["level"]);
            }
            else if(msgT == "handshake")
            {
                SendHandshake();
                ConsoleMessage("Handshaken");
            }
        }
        catch( Exception e )
        {
            ConsoleMessage( "JSON Parse Error, " + "Exception: " + e.Message );
            Shutdown();
        }
    }
    private void SendComplete( IAsyncResult ar ) // 보내기 완료시 불리는 이벤트
    {
        try
        {
            if( null == sock )
                return;

            int len = sock.EndSend( ar );
            ConsoleMessage( "Send success: " +len);
        }
        catch( Exception e )
        {
            ConsoleMessage( "Exception: " + e.Message );
            Shutdown();
        }
    }

    private void ConsoleMessage( string msg ) // 간단한 콘솔창에 메시지를 뿌림
    {             
        ConsoleTxts.Add(msg);
        if (ConsoleTxts.Count > 30)
        {
            ConsoleTxts.RemoveAt(0);
        }
        string outTxt = "";
        for (int i=0; i< ConsoleTxts.Count; ++i)
        {
            outTxt += ConsoleTxts[i] + "\n";
        }
        guiConsole.text = outTxt;
    }

    private void Shutdown()
    {
        if( sock != null )
        {
            sock.Shutdown( SocketShutdown.Both );
            sock = null;
        }
    }

    public static List<int> findOccurences(byte[] haystack, byte[] needle) // 간단한 byte 배열의 패턴을 다른 byte배열에서 찾는 루틴
    {
        List<int> occurences = new List<int>();

        int backup;
        for (int i = 0; i < haystack.Length; i++)
        {
            if (needle[0] == haystack[i])
            {
                backup = i;
                bool found = true;
                int j, k;
                for (j = 0, k = i; j < needle.Length; j++, k++)
                {
                    if (k >= haystack.Length || needle[j] != haystack[k])
                    {
                        found = false;
                        break;
                    }
                }
                if (found)
                {
                    occurences.Add(backup);
                    i = k;
                }
            }
        }
        return occurences;
    }

 
}

/*
 *        //ConsoleMessage(dataStr);
        /*bgm = (AudioClip)Resources.Load("BGM");
        audio.clip = bgm;
        audio.Play();
        */
