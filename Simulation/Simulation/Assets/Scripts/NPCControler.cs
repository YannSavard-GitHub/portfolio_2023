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

public class NPCControler : CharacterControler
{
    [SerializeField] GameObject Player;
    [SerializeField] Camera NPCHead;
    [SerializeField] Camera PlayerHead;
    public Vector3 directionNPC;
    public Vector3 directionNPCPlayer;
    public Vector3 rotationNPC = new Vector3(0, 5, 0);
    public bool shouldRotateNPC = false;
    public bool shouldMoveTowardPC = false; // PC= Player Character
    public bool shouldMoveForward = false; 
    public float directionSpeedNPC;
    // speed ratio - NPC speed= speedDiff_percent% of Player speed
    public float speedDiff_percent = 60.0f;

    //DetectPlayer method
    public Vector3 HeadNPCPosition; //direction foward.player
    public Vector3 sightDirectionNPC; //direction foward.player
    public Vector3 directionPlayer; // direction to Player
    public bool viewIsClear = false;
    public bool AngleIsValid = false;
    public bool playerDetected = false;

    //IdlePath method
    public float WalkTime = 5f; // time to walk - 3 seconds
    private float WalkTimeStart; // time at the beginning of movement.
    private bool timeSet = false; // if movement start time is set.
    private bool rotationSet = false; // if angle at start of rotation is set
    private bool StopRotation = false; 
    private Quaternion rotationEnd;

    // Start is called before the first frame update
    void Start()
    {
        shouldRotateNPC = false;
        shouldMoveTowardPC = false;
    }

    // Update is called once per frame
    void Update()
    {
        //ajust speed of NPC in function of Player's speed
        float weightRatio = GetComponent<Rigidbody>().mass / 
            Player.GetComponent<Rigidbody>().mass;

        directionSpeedNPC = ((directionSpeed * weightRatio) 
            / 100) * speedDiff_percent;

        //update NPC towards player direction
        directionNPCPlayer = PlayerHead.transform.position - 
            NPCHead.transform.position;

        // rotation
        if (shouldRotateNPC == true)
        {
            Rigidbody rb = GetComponent<Rigidbody>();
            base.RotateCharacter(rotationNPC, rb);
        }

        // move
        if (shouldMoveTowardPC == true)
        {
            transform.LookAt(Player.transform);
            base.MoveCharacter();   
        }
        // move
        if (shouldMoveForward == true)
        {
            MoveNPCCharacter(transform.forward);
        }

        // detect player
        AngleIsValid = ValidateViewAngle();    
        viewIsClear = ValidateClearView();

        if(AngleIsValid == true && viewIsClear == true)
        { 
            playerDetected = true; 
        }
		else
		{
            // NPC idle
            playerDetected = false;   
            IdlePath();
        }

        if(playerDetected == true)
		{
            //move towards player
            transform.LookAt(Player.transform);
            MoveNPCCharacter(directionNPCPlayer);
            //Debug.Log("Player Detected!");
        }         
    }

    public void MoveNPCCharacter( Vector3 _direction)
    {
        Rigidbody rb = GetComponent<Rigidbody>();
        rb.AddForce(_direction * directionSpeedNPC);
    }

    public bool ValidateViewAngle()
    {
        // returns true if view angle betweenNPC and Player is inferior as 90 degrees
        HeadNPCPosition = NPCHead.transform.position;

        Vector3 sightDirectionNPCTemp = NPCHead.transform.forward;
        Debug.DrawRay(HeadNPCPosition, sightDirectionNPCTemp, Color.green);

        Vector3 directionPlayerTemp = PlayerHead.transform.position - NPCHead.transform.position;
        Debug.DrawRay(HeadNPCPosition, directionPlayerTemp, Color.green);

        // dot product
        Vector3 sightDirectionNPC = sightDirectionNPCTemp - HeadNPCPosition;
        Vector3 directionPlayer = sightDirectionNPCTemp - HeadNPCPosition;
        return InferiorNeintyAngle(sightDirectionNPC, directionPlayer);

    }

    public static bool InferiorNeintyAngle(Vector3 _direction1, Vector3 _direction2)
	{
        // dot product
        if ((_direction1.x * _direction2.x +
                _direction1.y * _direction2.y +
                _direction1.z * _direction2.z) >= 0)
        {
            return true;
        }
        return false;

    }

    public bool ValidateClearView()
    //returns true if no objects are between head ofPlayer and NPC
    {
        Vector3 headNPCPos = NPCHead.transform.position;
        Vector3 PlayerHeadDir = PlayerHead.transform.position - NPCHead.transform.position;
        Debug.DrawRay(headNPCPos, PlayerHeadDir, Color.red);

        RaycastHit hit;
        if (Physics.Raycast(headNPCPos, Player.transform.position - transform.position, out hit))
        {
            if(hit.collider.gameObject.name == "Player")
			{
                return true;
            }    
        }
        return false;
    }
       
    public void IdlePath()
    {
        if(timeSet == false)
		{
            WalkTimeStart = Time.time; // time at the beginning of movement.
            timeSet = true;
        }
        float WalkTimeNow = Time.time - WalkTimeStart;
        if((WalkTimeNow >= WalkTime * 0.8f))
        {
            int angleDifference = 0; // difference between transform.rotation 
                                     // and EndRotation
            //set angle at start of rotation
            if (rotationSet == false)
			{
                rotationEnd = Quaternion.LookRotation(transform.forward * -1);
                rotationSet = true;
            }


            if (StopRotation ==false)
			{
                angleDifference = (int)Mathf.Abs(rotationEnd.eulerAngles.y - 
                    transform.rotation.eulerAngles.y);
            }

            if(angleDifference < Mathf.Round(rotationNPC.y))
            {
                StopRotation = true;
            }
			else
			{
                StopRotation = false;
            }
            //rotation
            if (StopRotation == false)
			{
                Rigidbody rb = GetComponent<Rigidbody>();
                RotateCharacter(rotationNPC, rb);
            }
            //stop moving
            if(WalkTimeNow >= WalkTime)
			{
                timeSet = false;
                StopRotation = false;
                rotationSet = false;
            }          
        }
		else
		{
            shouldMoveForward= true;
        }      
    }
}
