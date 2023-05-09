
/*****************************************************************************
* Project: Simulation
* File   : DoorOpener.cs
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
using System;
using UnityEngine;

public class DoorOpener : MonoBehaviour
{
    [SerializeField] Transform doorClosed;
    [SerializeField] Transform doorOpened;

    public enum doorStates {Closed, Opened, Moving};
    public doorStates doorState = doorStates.Closed;

    public enum doorTypes { Automatic, Interaction };
    public doorTypes doorType = doorTypes.Automatic;

    public float rotationSpeed = 0.007f; // speed of rotation
    public bool shouldClose = false;
    public bool shouldOpen = false;


    // Start is called before the first frame update
    void Start()
    {
    }

    // Update is called once per frame
    void Update()
    {
        //move door automatically
        if (shouldClose == true) Rotate(doorClosed);
        if (shouldOpen == true) Rotate(doorOpened);
    }

    void Rotate(Transform _doorState) 
    {
        transform.rotation = Quaternion.Lerp(transform.rotation, _doorState.rotation, rotationSpeed * Time.time);
        doorState = doorStates.Moving;
      
        if (_doorState == doorOpened)
        {
            if (Mathf.Round(transform.eulerAngles.y) == Mathf.Round(doorOpened.eulerAngles.y))
            {
                shouldOpen = false;
                doorState = doorStates.Opened;            
            }
        }
        if (_doorState == doorClosed)
        {
            if (Mathf.Round(transform.eulerAngles.y) == Mathf.Round(doorClosed.eulerAngles.y))
            {
                shouldClose = false;
                doorState = doorStates.Closed;        
            }
        }
    }
}
