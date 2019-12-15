using System.Collections.Generic;
using UnityEngine;
using SocketIO;

public class Socket_Client : MonoBehaviour
{

	// 在 Editor 里把 SocketIO 拖过来
	public SocketIOComponent sio;
	
	[SerializeField,Header("事件管理器")]
	GameObject ScreenClickedEventThrower;

	void Start()
	{
		if (sio == null)
			Debug.LogError("Drop a SocketIOComponent to Me!");
		// 声明 connect 事件和 server_sent 事件的回调函数
		sio.On("connect", OnConnect);
		sio.On("ai_move", ReceiveStep);
		sio.On("winner", ReceiveWinner);
	}
	void OnConnect(SocketIOEvent obj)
	{
		Debug.Log("Connection Open");
	}

	void ReceiveStep(SocketIOEvent obj)
	{
		JSONObject jsonObject = obj.data;
		string rcv = jsonObject.GetField("loc").str;
		Debug.Log("ai_move : " + rcv);
	}
	void ReceiveWinner(SocketIOEvent obj)
	{
		JSONObject jsonObject = obj.data;
		string rcv = jsonObject.GetField("winner").str;
		Debug.Log($"winner:{rcv}");
	}

	//btn
	public void pl_move(Vector2 loc)
	{
		Dictionary<string, string> data = new Dictionary<string, string>();
		data["loc"] = $"{loc.y},{loc.x}";
		sio.Emit("pl_move", new JSONObject(data));
	}
}
