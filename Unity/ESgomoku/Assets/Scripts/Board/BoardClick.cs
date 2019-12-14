using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using UnityEngine.UI;


public class BoardClick : MonoBehaviour
{
	[SerializeField,Header("棋盤")]
	GameObject board;
	[SerializeField]
	GameObject black_chess, white_chess;
	[SerializeField]
	GameObject unit_chess;

	[SerializeField]
	GameObject Socket_Client;

	bool isBlack = true;

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
			Debug.Log("Catch Event: BoardClick");
			Click();
			ScreenClickedEventThrower.GetComponent<ScreenClickedEvent>().mode = "pl_round";//改成已經輸入
		}
	}
	
	/////////////////////////private/////////////////////////////////
	void Click()
	{
		Vector2 pos = new Vector2((int)((Input.mousePosition.x - (board.transform.position.x - board.GetComponent<RectTransform>().rect.width / 2)) / unit_chess.GetComponent<RectTransform>().rect.width), (int)((Input.mousePosition.y - (board.transform.position.y - board.GetComponent<RectTransform>().rect.height / 2)) / unit_chess.GetComponent<RectTransform>().rect.width));
		Debug.Log($"Player Click : {pos}");
		Socket_Client.GetComponent<Socket_Client>().pl_move(pos);
		SummonChess(pos);
	}

	void SummonChess(Vector2 loc)
	{
		GameObject chess;
		if (isBlack)
		{
			chess = Instantiate(black_chess, board.transform);
		}
		else
		{
			chess = Instantiate(white_chess, board.transform);
		}
		isBlack = !isBlack;
		chess.transform.SetParent(board.transform);
		chess.GetComponent<RectTransform>().localPosition = loc * unit_chess.GetComponent<RectTransform>().rect.width - board.GetComponent<RectTransform>().rect.size/2 + unit_chess.GetComponent<RectTransform>().rect.size / 2;
	}
}
