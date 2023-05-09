/*****************************************************************************
* Project: Simulation
* File   : LightActivator.cs
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
* 03.11.2020	YS	Created
******************************************************************************/

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LightActivator : MonoBehaviour
{
    // both objects are used toguether as one light in the game
    [SerializeField] Light lightObject1 = null; 
    [SerializeField] Light lightObject2 = null;
    private bool lightsShouldTurnOff = false;

    // Start is called before the first frame update
    void Start()
    {
        lightObject1.intensity = 0f; //turn lights off
        lightObject2.intensity = 0f;
    }

    // Update is called once per frame
    void Update()
    {
        //close lights if character in front of the building 
        // and went back, but is still in the trigger perimeter.
        if (lightsShouldTurnOff == true && lightObject1.intensity == 1.4f)
		{
            lightObject1.intensity = 0f; //turn lights off
            lightObject2.intensity = 0f;
            lightsShouldTurnOff = false;
        }    
    }

    private void OnTriggerEnter(Collider other)
    {
        //if object is in front of the building
        if (other.transform.position.z < -591.4083f)
		{
            if (lightObject1.intensity == 0f) //if lights are off
            {
                lightObject1.intensity = 1.4f; //turn lights on
                lightObject2.intensity = 1.4f;
            }            
        }   
    }

    private void OnTriggerExit(Collider other)
    {
        lightObject1.intensity = 0f; //turn lights off
        lightObject2.intensity = 0f;
    }

    private void OnTriggerStay(Collider other)
    {
        //if object is at the front (including sides) of the building
        if (other.transform.position.z < -591.4083f)
        // -591.4083f = Player's position.z right in front of the door
        {
            lightObject1.intensity = 1.4f; //turn lights on
            lightObject2.intensity = 1.4f;
        }
    }
}
