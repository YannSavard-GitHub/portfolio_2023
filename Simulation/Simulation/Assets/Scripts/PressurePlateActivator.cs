/*****************************************************************************
* Project: Simulation
* File   : PressurePlateActivator.cs
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
* +-03.11.2020  YS	Created
******************************************************************************/
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PressurePlateActivator : MonoBehaviour
{
    [SerializeField] DoorOpener doorOpener = null;
    [SerializeField] AudioClip doorSound;
    public AudioSource audioSource;

    public bool pressurePlateDown = false;
    public bool pressurePlateUp = false;
   
    public float timeStart = 0f;
    public float timeNow = 0f;
    public float scaleValueMax = 0.25f;
    public float scaleValueMin = 0.001f;
    public float scaleValueNow = 0.001f;
    public float scaleTime = 10.0f;
    public float scaleTimeRatio = 0;

    // Start is called before the first frame update
    void Start()
    {
        scaleValueMax = transform.localScale.y;
        //AudioSource audioSource = GetComponent<AudioSource>();
        audioSource.clip = doorSound;
    }

    // Update is called once per frame
    void Update()
    {
        scaleValueNow = transform.localScale.y;
      
        if (pressurePlateDown == true)
        {
            audioSource.Play();

            float scaleValueY = Mathf.Lerp(scaleValueNow, scaleValueMin, Time.deltaTime * scaleTime);
            transform.localScale = new Vector3(transform.localScale.x, scaleValueY, transform.localScale.x);

            if (scaleValueY < scaleValueMin + scaleValueMax * 0.10f) // if pressure plate is 90% closed
            {
                pressurePlateDown = false;
                if (doorOpener.doorState == DoorOpener.doorStates.Opened) doorOpener.shouldClose = true;
                if (doorOpener.doorState == DoorOpener.doorStates.Closed) doorOpener.shouldOpen = true;
            }
        }
        if (pressurePlateUp == true)
        {
            float scaleValueY = Mathf.Lerp(scaleValueNow, scaleValueMax, Time.deltaTime * scaleTime);
            transform.localScale = new Vector3(transform.localScale.x, scaleValueY, transform.localScale.x);

            if (scaleValueY > scaleValueMax - scaleValueMax * 0.10f)
            {
                pressurePlateUp = false;
            }
        }
    }
    private void OnTriggerEnter(Collider other)
    {
        pressurePlateUp = false;
        pressurePlateDown = true;     
    }

    private void OnTriggerExit(Collider other)
    {
        pressurePlateDown = false;
        pressurePlateUp = true;    
    }
}
