/*****************************************************************************
* Project: Simulation
* File   : ChocolateDisposer.cs
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

public class ChocolateDisposer : MonoBehaviour
{
    [SerializeField] AudioClip eatingEnjoyingSound;
    public AudioSource audioSource;
      
    // Start is called before the first frame update
    void Start()
    {
        audioSource= GameObject.Find("Player").GetComponent<AudioSource>();
        audioSource.clip = eatingEnjoyingSound;
    }

    // Update is called once per frame
    void Update()
    {
    }

	private void OnCollisionEnter(Collision collision)
	{
        audioSource.Play();
        gameObject.SetActive(false);        
    }
}
