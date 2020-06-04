using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using UnityEngine.UI;


public class BoardClick : MonoBehaviour
{
	[SerializeField, Header("棋盤")]
	GameObject board;
	[SerializeField, Header("棋盤範圍")]
	GameObject touchpad;
	[SerializeField]
	GameObject black_chess, white_chess;
	[SerializeField]
	GameObject unit_chess;

	[SerializeField]
	GameObject Socket_Client;

	public bool isBlack = true;
	public bool[,] has_chess;


	[SerializeField, Header("棋盤顏色(正常)")]
	Color boardColor;
	[SerializeField, Header("棋盤顏色(拒絕輸入)")]
	Color boardColor2;

	[SerializeField,Header("玩家頭像外框")]
	GameObject player_Boarder0, player_Boarder1;
	[SerializeField, Header("玩家外框色顏色(可以落子)")]
	Color PlayerColor;
	[SerializeField, Header("玩家外框色顏色(等待)")]
	Color PlayerColor2;

	////////////////////////////////////////////

	[SerializeField, Header("事件投擲器"), Tooltip("螢幕點擊事件投擲器")]
	GameObject ScreenClickedEventThrower;
	private void Awake()
	{
		ScreenClickedEventThrower.GetComponent<ScreenClickedEvent>().ScreenClicked += OnClick;//向Event Thrower訂閱事件
	}

	private void OnDestroy()
	{
		ScreenClickedEventThrower.GetComponent<ScreenClickedEvent>().ScreenClicked -= OnClick;//向Event Thrower取消訂閱事件
	}

	// Start is called before the first frame update
	void Start()
	{
		has_chess = new bool[9, 9];
		ShowPlayerTurn();
	}

	// Update is called once per frame
	void Update()
	{

	}
	/////////////////////////public//////////////////////////////////
	public void OnClick(object sender, EventArgs e)
	{
		if (ScreenClickedEventThrower.GetComponent<ScreenClickedEvent>().mode == "pl_round")//允許輸入
		{
			//Debug.Log("Catch Event: BoardClick");
			Click();
		}
	}

	public void LockBoard()
	{
		ScreenClickedEventThrower.GetComponent<ScreenClickedEvent>().mode = "locked";
		board.GetComponent<Image>().color = boardColor2;
	}

	public void UnlockBoard()
	{
		ScreenClickedEventThrower.GetComponent<ScreenClickedEvent>().mode = "pl_round";
		board.GetComponent<Image>().color = boardColor;
	}

	public void SummonChess(Vector2 loc)
	{
		GameObject chess;
		if (isBlack)
		{
			chess = Instantiate(black_chess, touchpad.transform);
		}
		else
		{
			chess = Instantiate(white_chess, touchpad.transform);
		}
		chess.transform.SetParent(touchpad.transform);
		//chess.GetComponent<RectTransform>().localPosition = loc * unit_chess.GetComponent<RectTransform>().rect.width - touchpad.GetComponent<RectTransform>().rect.size / 2 + unit_chess.GetComponent<RectTransform>().rect.size / 2;
		chess.GetComponent<RectTransform>().localPosition = loc * unit_chess.GetComponent<RectTransform>().rect.width - touchpad.GetComponent<RectTransform>().rect.size / 2 + unit_chess.GetComponent<RectTransform>().rect.size;

		isBlack = !isBlack;
		ShowPlayerTurn();
	}

	/////////////////////////private/////////////////////////////////
	void Click()
	{
		//Vector2 pos = new Vector2((int)((Input.mousePosition.x - (touchpad.transform.position.x - touchpad.GetComponent<RectTransform>().rect.width / 2)) / unit_chess.GetComponent<RectTransform>().rect.width), (int)((Input.mousePosition.y - (touchpad.transform.position.y - touchpad.GetComponent<RectTransform>().rect.height / 2)) / unit_chess.GetComponent<RectTransform>().rect.width));
		Vector2 pos = new Vector2((int)((Input.mousePosition.x - (touchpad.transform.position.x - touchpad.GetComponent<RectTransform>().rect.width / 2)- unit_chess.GetComponent<RectTransform>().rect.width/2 ) / unit_chess.GetComponent<RectTransform>().rect.width), (int)((Input.mousePosition.y - (touchpad.transform.position.y - touchpad.GetComponent<RectTransform>().rect.height / 2) - unit_chess.GetComponent<RectTransform>().rect.height / 2) / unit_chess.GetComponent<RectTransform>().rect.width));

		if (0 <= pos.x && pos.x < 9 && 0 <= pos.y && pos.y < 9 && !has_chess[(int)pos.x, (int)pos.y])
		{
			ScreenClickedEventThrower.GetComponent<ScreenClickedEvent>().mode = "ai_round";//改成已經輸入

			//Debug.Log($"Player Click : {pos}");
			has_chess[(int)pos.x, (int)pos.y] = true;
			Socket_Client.GetComponent<Socket_Client>().pl_move(pos);
			SummonChess(pos);
		}
	}

	void ShowPlayerTurn()
	{
		player_Boarder0.GetComponent<Image>().color = (isBlack) ? PlayerColor : PlayerColor2;
		player_Boarder1.GetComponent<Image>().color = (!isBlack) ? PlayerColor : PlayerColor2;
	}
}
