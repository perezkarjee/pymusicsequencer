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
    public void Test1() // 걍 텍스트 에코 테스트
    {
        JSONCon dict = Dict();
        dict.Set("msgtype", Str("txt"));
        dict.Set("txt", Str("텍스트"));
        JSONCon list = List();
        list.Add(Int(1));
        list.Add(Int(2));
        list.Add(Int(3));
        list.Add(Int(4));
        list.Add(Int(5));
        dict.Set("testList", list);

        Send(dict);

    }
        //ConsoleMessage(dataStr);
        /*bgm = (AudioClip)Resources.Load("BGM");
        audio.clip = bgm;
        audio.Play();
        */
    public void Test2()
    {
        JSONCon dict = Dict();
        dict.Set("msgtype", Str("login"));
        dict.Set("acc", Str("아이디"));
        dict.Set("pw", Str("비번"));

        Send(dict);

        TestStruct ts = new TestStruct();
        ts.name = "이름";
        ts.level = 10;
        JSONCon dict2 = Dict();
        dict2.Set("msgtype", Str("txtpluslevel"));
        dict2.Set("txt", Str(ts.name));
        dict2.Set("level", Int(ts.level));
        Send(dict2);
    }
    public void SendHandshake()
    {
        string hsMsg = "THEPGAMERPG";
        JSONCon dict = Dict();
        dict.Set("msgtype", Str("handshake"));
        dict.Set("hs", Str(hsMsg));
        Send(dict);
    }

    string Conv(JSONCon data)
    {
        return JSONCon.ConvertToJSON(data);
    }
    JSONCon Dict()
    {
        return JSONCon.GetDict();
    }
    JSONCon List()
    {
        return JSONCon.GetList();
    }
    JSONCon Float(int val)
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
        /*
        if (line[0] == 0)
        {
            string strTxt = Encoding.UTF8.GetString(line, 1, line.Length-1);
            ConsoleMessage(String.Format("에코: " + strTxt));
        }
        else if (line[0] == 1)
        {

            byte[] levelb = new byte[4];
            Buffer.BlockCopy(line, 1, levelb, 0, 4); 
            int level = BitConverter.ToInt32(levelb, 0);

            byte[] strLenb = new byte[4];
            Buffer.BlockCopy(line, 1+4, strLenb, 0, 4); 
            int strLen = BitConverter.ToInt32(strLenb, 0);

            byte[] txt = new byte[line.Length-1-4-4];
            Buffer.BlockCopy(line, 1+4+4, txt, 0, strLen); 
            string strTxt = Encoding.UTF8.GetString(txt);

            ConsoleMessage(String.Format("레벨: {0} 문자열길이(byte): {1} 문자열: {2}", level, strLen, strTxt));
        }*/
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
 */
