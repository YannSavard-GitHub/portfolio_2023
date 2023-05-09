/*****************************************************************************
* Project: Simulation
* File   : NPCControler.cs
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

public class CharacterControler : MonoBehaviour
{
    public Vector3 direction;
    public float directionSpeed = 750.0f;
    public Vector3 rotation;
    public bool shouldRotate = false;
    public bool shouldMove = false;

    Animator state; 

    // Start is called before the first frame update
    void Start()
    {
        state = GetComponent<Animator>();     
    }

    // Update is called once per frame
    void Update()
     {
        shouldMove = shouldRotate = false;

        //Move Character
        if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow))
        {
            shouldMove = true;
            direction = transform.forward;
        }
        if (Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow))
        {
            shouldMove = true;
            direction = -transform.forward;
        }

        //Rotate Character
        if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow))
        {
            shouldRotate = true;
            rotation = new Vector3(0, -3, 0);
        }
        if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow))
        {
            shouldRotate = true;
            rotation = new Vector3(0, 3, 0);
        }

        if (Input.GetKeyUp(KeyCode.A) || Input.GetKeyUp(KeyCode.D)) shouldRotate = false;
        if (Input.GetKeyUp(KeyCode.W) || Input.GetKeyUp(KeyCode.S))
        {
            shouldMove = false;
        }
        Rigidbody rb = GetComponent<Rigidbody>();
        if (shouldRotate == true) RotateCharacter(rotation, rb);
        if (shouldMove == true) MoveCharacter();
    }

    public void RotateCharacter(Vector3 _rotation, Rigidbody _rb)
    {
        //state.runtimeAnimatorController.animationClips[0]. = state.runtimeAnimatorController.animationClips[1];

        Quaternion newRotation = Quaternion.Euler(_rotation);
        _rb.freezeRotation = false;
        Quaternion.Lerp(transform.rotation, newRotation, _rotation.y * Time.deltaTime);
        transform.Rotate(_rotation);
        _rb.freezeRotation = true;
    }

    public virtual void MoveCharacter()
        {
            Rigidbody rb = GetComponent<Rigidbody>();
            rb.AddForce(direction * directionSpeed);
        }
}

//s-115,w-119