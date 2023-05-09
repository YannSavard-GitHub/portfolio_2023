/*****************************************************************************
* Project: Simulation
* File   : DoorActivator.cs
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
using TMPro;
using UnityEngine;

public class DoorActivator : MonoBehaviour
{
    [SerializeField] DoorOpener doorOpener;
    [SerializeField] GameObject doorGUICanvas;

    [SerializeField] AudioClip doorSound;
    [SerializeField] AudioSource audioSource;

    // Start is called before the first frame update
    void Start()
    {
        // GUI
        doorGUICanvas.SetActive(false);
        // Sound effect
        audioSource.clip = doorSound;
    }

    // Update is called once per frame
    void Update()
    {      
    }

    private void OnTriggerEnter(Collider other)
    {
        if(other.name == "Player")
		{
            if (doorOpener.doorType == DoorOpener.doorTypes.Automatic)
            {
                if (doorOpener.doorState == DoorOpener.doorStates.Closed)
                {
                    doorOpener.shouldOpen = true;
                    doorOpener.shouldClose = false;
                    // Sound Effect
                    audioSource.Play();
                }
            }      
        } 
    }

    private void OnTriggerExit(Collider other)
    {
        // automatic type door
        if (other.name == "Player")
        {
            if (doorOpener.doorType == DoorOpener.doorTypes.Automatic)
            {
                if (doorOpener.doorState == DoorOpener.doorStates.Opened)
                {
                    doorOpener.shouldOpen = false;
                    doorOpener.shouldClose = true;
                    // Sound Effect
                    audioSource.Play();
                }
            }

            // interaction type door
            if (doorOpener.doorType == DoorOpener.doorTypes.Interaction)
            {
                if (doorGUICanvas.activeSelf == true)
                {
                    doorGUICanvas.SetActive(false);
                }
            }
        }           
    }

	private void OnTriggerStay(Collider other)
	{
        if (other.name == "Player")
        {
            if (doorOpener.doorType == DoorOpener.doorTypes.Interaction)
            {
                // show instruction message 
                if (doorOpener.doorState == DoorOpener.doorStates.Closed)
                {
                    doorGUICanvas.SetActive(true);
                }
                else
                {
                    doorGUICanvas.SetActive(false);
                }

                if (Input.GetKey(KeyCode.Space))
                {
                    // activate door
                    if (doorOpener.doorState == DoorOpener.doorStates.Closed)
                    {
                        doorOpener.shouldClose = false;
                        doorOpener.shouldOpen = true;
                    }
                    else if (doorOpener.doorState == DoorOpener.doorStates.Opened)
                    {
                        doorOpener.shouldOpen = false;
                        doorOpener.shouldClose = true;
                    }
                    // Sound Effect
                    audioSource.Play();
                }
            }
        }  
    }
}
