using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using SocketIO;
using System.Threading;

public class Socket_Client : MonoBehaviour
{

	// 在 Editor 里把 SocketIO 拖过来
	public SocketIOComponent sio;

	[SerializeField, Header("事件管理器")]
	GameObject ScreenClickedEventThrower;

	[SerializeField, Header("顯示判斷結果")]
	GameObject analyze_text;

	[SerializeField, Header("棋盤")]
	GameObject board;

	[SerializeField, Header("棋盤程式碼")]
	GameObject boardClick;

	System.Diagnostics.Process process;

	private void Awake()
	{
		System.Diagnostics.ProcessStartInfo Info2 = new System.Diagnostics.ProcessStartInfo();

		Info2.FileName = "server.bat";//執行的檔案名稱
		Info2.WorkingDirectory = @"./Assets/scripts/System";

		System.Diagnostics.Process.Start(Info2);
		Debug.Log("server opened!");
	}

	void Start()
	{
		//總之先鎖住鍵盤再說
		boardClick.GetComponent<BoardClick>().LockBoard();

		if (sio == null)
			Debug.LogError("Drop a SocketIOComponent to Me!");
		// 声明 connect 事件和 server_sent 事件的回调函数
		sio.On("connect", OnConnect);
		sio.On("ai_move", ReceiveStep);
		sio.On("judge", ReceiveJudge);
		sio.On("pl_turn", ReceiveCanMove);
		sio.On("winner", ReceiveWinner);
	}

	private void OnDestroy()
	{
		sio.Emit("disconnect");
	}


	void OnConnect(SocketIOEvent obj)//連接成功
	{
		//Debug.Log("Connection Open");
		analyze_text.GetComponent<Text>().text = "";
	}

	void ReceiveStep(SocketIOEvent obj)//收到電腦落子位置
	{
		JSONObject jsonObject = obj.data;
		string rcv = jsonObject.GetField("loc").str;
		Debug.Log("ai_move : " + rcv);
	}

	void ReceiveJudge(SocketIOEvent obj)//伺服器處理完畢，允許玩家落子
	{
		JSONObject jsonObject = obj.data;
		string rcv = jsonObject.GetField("value").str;

		//顯示結果
		string value = "";
		string[] pattern_name = { "五連", "活四", "活三", "活二", "跳四(長邊)", "跳四(短邊)", "跳四(中間)", "死四", "跳三(長邊)", "跳三(短邊)", "跳三(長邊死, 長邊)", "跳三(短邊死, 長邊)", "跳三(長邊死, 短邊)", "跳三(短邊死, 短邊)", "死三", "跳二", "弱活二", "死二" };
		for (int i = 0; i < rcv.Length; i++)
		{
			if (rcv[i] != '0')
			{
				value += $"{pattern_name[i]}:{rcv[i]}\n";
			}
		}
		analyze_text.GetComponent<Text>().text = value;
	}

	void ReceiveCanMove(SocketIOEvent obj)//伺服器處理完畢，允許玩家落子
	{
		ScreenClickedEventThrower.GetComponent<ScreenClickedEvent>().mode = "pl_round";//改成允許輸入
		boardClick.GetComponent<BoardClick>().UnlockBoard();

	}

	void ReceiveWinner(SocketIOEvent obj)//收到勝者，遊戲結束
	{
		JSONObject jsonObject = obj.data;
		string rcv = jsonObject.GetField("winner").str;
		Debug.Log($"winner:{rcv}");
		analyze_text.GetComponent<Text>().text += $"\n\n{rcv}";
	}

	//btn
	public void pl_move(Vector2 loc)
	{
		Dictionary<string, string> data = new Dictionary<string, string>();
		data["loc"] = $"{loc.y},{loc.x}";
		sio.Emit("pl_move", new JSONObject(data));

		//顯示結果
		analyze_text.GetComponent<Text>().text = "...";
		boardClick.GetComponent<BoardClick>().LockBoard();
	}
}
