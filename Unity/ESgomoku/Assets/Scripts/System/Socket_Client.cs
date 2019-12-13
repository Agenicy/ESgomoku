using System.Collections.Generic;
using UnityEngine;
using SocketIO;

public class Socket_Client : MonoBehaviour
{

	// 在 Editor 里把 SocketIO 拖过来
	public SocketIOComponent sio;
	void Start()
	{
		if (sio == null)
			Debug.LogError("Drop a SocketIOComponent to Me!");
		// 声明 connect 事件和 server_sent 事件的回调函数
		sio.On("connect", OnConnect);
		sio.On("server_sent", OnReceive);
	}
	/// <summary>
	/// connect 事件的回调函数
	/// </summary>
	/// <param name="obj"></param>
	void OnConnect(SocketIOEvent obj)
	{
		Debug.Log("Connection Open");
		OnReceive(obj);
	}
	/// <summary>
	/// 接收到 server_sent 事件的回调函数
	/// </summary>
	/// <param name="obj">SocketIOEvent</param>
	void OnReceive(SocketIOEvent obj)
	{
		// 1. 接收并输出 Server 传递过来的数字
		JSONObject jsonObject = obj.data;
		string rcv_nbr = jsonObject.GetField("nbr").str;
		Debug.Log("Recieved From Server : " + rcv_nbr);
		// 2. 将数字 +1 并返回给 Server
		try
		{
			int int_nbr = int.Parse(rcv_nbr);
			SendToServer(int_nbr + 1);
		}
		catch
		{
		}
	}
	/// <summary>
	/// 将数字发给 Server
	/// </summary>
	/// <param name="_nbr">发送的数字</param>
	void SendToServer(int _nbr)
	{
		Dictionary<string, string> data = new Dictionary<string, string>();
		data["nbr"] = _nbr.ToString();
		sio.Emit("client_sent", new JSONObject(data));
	}
}
