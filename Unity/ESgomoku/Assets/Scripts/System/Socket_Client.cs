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
		sio.On("pl_turn", ReceiveCanMove);
		sio.On("winner", ReceiveWinner);
	}
	void OnConnect(SocketIOEvent obj)//連接成功
	{
		Debug.Log("Connection Open");
	}

	void ReceiveStep(SocketIOEvent obj)//收到電腦落子位置
	{
		JSONObject jsonObject = obj.data;
		string rcv = jsonObject.GetField("loc").str;
		Debug.Log("ai_move : " + rcv);
	}

	void ReceiveCanMove(SocketIOEvent obj)//伺服器處理完畢，允許玩家落子
	{
		ScreenClickedEventThrower.GetComponent<ScreenClickedEvent>().mode = "pl_round";//改成允許輸入

		Debug.Log("your turn ...");
	}

	void ReceiveWinner(SocketIOEvent obj)//收到勝者，遊戲結束
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
