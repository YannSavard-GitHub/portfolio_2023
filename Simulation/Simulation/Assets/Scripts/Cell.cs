/*****************************************************************************
* Project: Simulation
* File   : Cell.cs
* Date   : 17.11.2020
* Author : Yann Savard (YS)
*
* These coded instructions, statements, and computer programs contain
* proprietary information of the author and are protected by Federal
* copyright law. They may not be disclosed to third parties or copied
* or duplicated in any form, in whole or in part, without the prior
* written consent of the author.
*
* History:
* +-17.11.2020	YS	Created
******************************************************************************/
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Cell : MonoBehaviour
{
    [SerializeField] public GameObject pillar;
    [SerializeField] public GameObject chocolateBar;

    private int state { get; set; }//1 = true; 0 = false
    public bool neighbour1 = false;
    public bool neighbour2 = false;
    public bool neighbour3 = false;
    public bool neighbour4 = false;
    public (int, int) Indexes = (0, 0);
    public Vector3 position = new Vector3(0,0,0);

    // Start is called before the first frame update
    void Start()
    {
        state = 1;
    }

    // Update is called once per frame
    void Update()
    {
        // activate and deactivate Pillar objects
        if(state== 0)
		{
            pillar.SetActive(true);
        }
		else
		{
            pillar.SetActive(false);
        } 
    }
}
