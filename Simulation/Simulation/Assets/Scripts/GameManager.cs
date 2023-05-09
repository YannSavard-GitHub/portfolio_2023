/*****************************************************************************
* Project: Simulation
* File   : GameManager.cs
* Date   : 03.11.2020
* Author : Yann Savard (YS)
*
* These coded instructions, statements, and computer programs contain
* proprietary information of the author and are protected by Federal
* copyright law. They may not be disclosed to third parties or copied
* or duplicated in any form, in whole or in part, without the prior
* written consent of the author.
*
* History:
* +-25.10.2020	YS	Created
******************************************************************************/
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameManager : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        //Move Character
        if (Input.GetKey(KeyCode.Escape))
        {
            Application.Quit();
        }
    }
}
