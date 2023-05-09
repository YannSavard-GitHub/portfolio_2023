/*****************************************************************************
* Project: Simulation
* File   : LabyrinthGenerator.cs
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
using System.Collections.Generic;
using UnityEngine;


public class LabyrinthGenerator : MonoBehaviour
{
    [SerializeField] Cell baseCell;
    [SerializeField] Cell chocCell;

    [SerializeField] GameObject sphere1;
    [SerializeField] GameObject sphere2;
    [SerializeField] GameObject sphere3;
    
    [SerializeField] int cellWidthX = 18; // must be smaller then 18
    [SerializeField] int cellLenghtZ = 28; // must be smaller then 28

    // indexes and states of cells (from the labyrinth grid)
    public Dictionary<(int, int), Cell> idxCellDict;
    public Dictionary<(int, int), int> stateDict;

    //positions for indexes of idxStateDict
    public Dictionary<(int, int),Vector3> idxPosCellsDict;
    public Dictionary<(int, int), Vector3> idxPosChocDict;

    //recursive backtracking - FindNeighbourCells method
    public (int, int) previousCell = (-1, -1);
    public Stack<(int, int)> positionStack; // indexes of cells 
    public int baseCellX = 9; // first cell indexes at the entrance of labyrinth
    public int baseCellZ = 2; 
    public bool stopPush = false;

    //SpawnChocolate method
    public int ChocBarsMax = 0; // number of chocolate bars in labyrinth
    public int ChocBarsNumber; //to be generated randomly

    //total labyrinth free cells
    public int labyrinthFreeCells;
    public float freeCellsPourcentage = 0.535f;

    // Start is called before the first frame update

    void Start()
    {
        idxCellDict = new Dictionary<(int, int), Cell>(); 
        idxPosCellsDict= new Dictionary<(int, int), Vector3>();
        idxPosChocDict= new Dictionary<(int, int), Vector3>();
        stateDict = new Dictionary<(int, int), int>();
        positionStack = new Stack<(int, int)>();

        bool validLabyrinth = false;
        while(validLabyrinth == false)
		{
            CreateCellList();
            GenerateLabyrinth();

            bool labyrinth = ValidateLabyrinth();

            if (labyrinth == true)
            {
                validLabyrinth = true;
            }
			else
			{
                //restart process - generate new labyrinth
                ClearLabyrinthValues();
            }
        }
        SpawnPillars();
        SpawnChocolate();
    }

    public void CreateCellList()
	{
        //calculate distance between each cell 
        //rows 
        float distX = (sphere2.transform.position.x - sphere1.transform.position.x) / cellWidthX;
        //coloms
        float distZ = (sphere3.transform.position.z - sphere1.transform.position.z) / cellLenghtZ; 

        float cellPosX;
        float cellPosY;
        float cellPosZ;

        float chocPosX;
        float chocPosY;
        float chocPosZ;

        Vector3 cellPosition = new Vector3();
        Vector3 chocPosition = new Vector3();
        Cell newCell = baseCell;
        Cell newChoc = chocCell;
        
        for (int idxZ = 0; idxZ < cellLenghtZ; idxZ++)
        {
            for (int idxX = 0; idxX < cellWidthX; idxX++)
            {
                cellPosX = newCell.transform.localPosition.x + distX * idxX;
                cellPosY = newCell.transform.localPosition.y;
                cellPosZ = newCell.transform.localPosition.z + distZ * idxZ;

                chocPosX = chocCell.transform.localPosition.x + distX * idxX;
                chocPosY = chocCell.transform.localPosition.y;
                chocPosZ = chocCell.transform.localPosition.z + distZ * idxZ;

                cellPosition = new Vector3(cellPosX, cellPosY, cellPosZ);
                chocPosition = new Vector3(chocPosX, chocPosY, chocPosZ);
                //add cells to dictionary and assign state=false to all of them (empty clear grid)

                idxCellDict.Add((idxX, idxZ), newCell);
                stateDict.Add((idxX, idxZ), 1);
                //add indexes of positions to dictionary
                idxPosCellsDict.Add((idxX, idxZ), cellPosition);
                idxPosChocDict.Add((idxX, idxZ), chocPosition);
                //add attributes to cell
                //
                newCell.Indexes = (idxX, idxZ);
                newCell.position = cellPosition; 
            }   
        }
    }

    public void GenerateLabyrinth()
	{
		//fill all contours
		for (int idxX = 0; idxX < cellWidthX; idxX++)
		{
			stateDict[(idxX, 0)] = 0;
			stateDict[(idxX, cellLenghtZ)] = 0;
		}
		for (int idxZ = 0; idxZ < cellLenghtZ; idxZ++)
		{
			stateDict[(0, idxZ)] = 0;
			stateDict[(cellWidthX, idxZ)] = 0;
		}
        // free cell at the entrance 
        stateDict[(baseCellX, baseCellZ)] = 0;

        // add first cell to stack
        if (previousCell != (-1,-1))
		{
            positionStack.Push(previousCell); 
        }

        FindNeighbourCell(baseCellX, baseCellZ); // search for neighbour cells and add indexes to Stack and Dictionary
        ManageStacks();

        // set labyrinth temporary objeccts inactive
        GameObject[] tempObjects;
        tempObjects = GameObject.FindGameObjectsWithTag("Temporary");
        foreach (GameObject tempObject in tempObjects)
        {
            tempObject.SetActive(false);
        }

    }

    public void ClearLabyrinthValues()
	{
        //destroy objects and reset values to enable new labrinth generation

        GameObject[] baseCells;
        baseCells = GameObject.FindGameObjectsWithTag("baseCell");

        foreach (GameObject baseCell in baseCells)
        {
            Destroy(baseCell);
        }

        GameObject[] chocCells;
        chocCells = GameObject.FindGameObjectsWithTag("chocCell");

        foreach (GameObject chocCell in chocCells)
        {
            Destroy(chocCell);
        }

        GameObject[] chocBars;
        chocBars = GameObject.FindGameObjectsWithTag("chocBar");

        foreach (GameObject chocBar in chocBars)
        {
            Destroy(chocCell);
        }

        stateDict.Clear();
        idxCellDict.Clear();
        idxPosCellsDict.Clear();
		idxPosCellsDict.Clear();
		idxPosChocDict.Clear();
		//reset positionStack 
		positionStack.Clear();
		previousCell = (-1, -1);
        stopPush = false;
    }

    public bool ValidateLabyrinth()
    {
        labyrinthFreeCells = 0;
        for (int idxX = 0; idxX < cellWidthX; idxX++)
        {
            for (int idxZ = 0; idxZ < cellLenghtZ; idxZ++)
            // 0 and -1 on the Z axis are the empty sides.
            {
                if (stateDict[(idxX, idxZ)] == 0) // if two empty spaces are available in labyrint
                {
                    labyrinthFreeCells++;
                }
            }
        }
        //if freeCellsPourcentage of cells in stateDict are free, labyrinth is valid
        if (labyrinthFreeCells >= stateDict.Count * freeCellsPourcentage) 
        {           
            return true;
        }
        else
        {
            return false;
        }
    }

    public void ManageStacks()
	{
        stopPush = true;
        positionStack.Pop(); // pop first cell from Stack- 

        while (positionStack.Count > 0)
        {
            (int, int) cell = positionStack.Pop();
            FindNeighbourCell(cell.Item1, cell.Item2);        
        }
    }

    public (int, int) FindNeighbourCell(int _idxX, int _idxZ)//returns state of cell
    {
        List<(int, int)> validNeighbours = new List<(int, int)>();
        List<(int, int)> directNeighbours = new List<(int, int)>();

        (int, int) neighbour = (-1, -1);
        (int, int) directNeighbour = (-1, -1);
        previousCell = (_idxX, _idxZ);
    
        if (previousCell == (-1, -1)) // exit condition 1
        {
            return (-1, -1);
        }

        //get coordinates of potentially valid neighbour cells
        //verify validity of positions

        bool validatePos = ValidatePosition(_idxX + 2, _idxZ);
        if (validatePos == true)
        {
            if (stateDict[(_idxX + 2, _idxZ)] == 1)
            {
                validNeighbours.Add((_idxX + 2, _idxZ));
                directNeighbours.Add((_idxX + 1, _idxZ));
            }
        }
        validatePos = ValidatePosition(_idxX - 2, _idxZ);
        if (validatePos == true)
        {
            if (stateDict[(_idxX - 2, _idxZ)] == 1)
            {
                validNeighbours.Add((_idxX - 2, _idxZ));
                directNeighbours.Add((_idxX - 1, _idxZ));
            }
        }
        validatePos = ValidatePosition(_idxX, _idxZ + 2);
        if (validatePos == true)
        {
            if (stateDict[(_idxX, _idxZ + 2)] == 1)
            {
                validNeighbours.Add((_idxX, _idxZ + 2));
                directNeighbours.Add((_idxX, _idxZ + 1));
            }
        } 
        validatePos = ValidatePosition(_idxX, _idxZ - 2);
        if (validatePos == true)
        {
            if (stateDict[(_idxX, _idxZ - 2)] == 1)
            {
                validNeighbours.Add((_idxX, _idxZ - 2));
                directNeighbours.Add((_idxX, _idxZ - 1));
            }
        }
        
        //generate random valid neighbour
        if (validNeighbours.Count > 0)
        {
            bool valid = false;
            while (valid == false)
            {              
                int neighbourInt = UnityEngine.Random.Range(0, validNeighbours.Count);
               
                if (validNeighbours[neighbourInt] != (-1, -1))
                {
                    //get random neighbour index and its direct neighbour 
                    neighbour = validNeighbours[neighbourInt];
                    directNeighbour = directNeighbours[neighbourInt];
                    valid = true;
                }
            }
        }
        else  //exit condition 2 - no neighbours were found;
        {
            return (-1, -1);
        }

        validNeighbours.Clear();
        directNeighbours.Clear();

        //Add positions to the Stack and update Dictionary stateDict values.
        AddNeighbourCells(neighbour, directNeighbour);


        previousCell = (neighbour);
        //recursive call
        return FindNeighbourCell(neighbour.Item1, neighbour.Item2);
    }

    public void AddNeighbourCells((int, int) _neighbour, (int, int) _directNeighbour)
	{
        //push indexes into the stack
        if(stopPush == false)
		{
            positionStack.Push(_neighbour);
        }
   
      
        //change values in Dictionary
        stateDict[_neighbour] = 0;
        stateDict[_directNeighbour] = 0;
    }

    public void SpawnPillars()
    {
        for (int idxZ = 1; idxZ < cellLenghtZ; idxZ++)
        {
            for (int idxX = 1; idxX < cellWidthX; idxX++)
            {
                if (stateDict[(idxX, idxZ)] == 1)
                {
                    //Instanciate GameObject pillar  of the cell
                    Instantiate(idxCellDict[(idxX, idxZ)], idxPosCellsDict[(idxX, idxZ)],
                    baseCell.transform.rotation);
                }
            }
        }
    }

    public void SpawnChocolate()
	{
        List<Vector3> validSpawnPosList = new List<Vector3>();

        //get valid spawning positions
        for (int idxX = 1; idxX < cellWidthX - 2; idxX++)
        // -2, so that the chocolate bar 
        //has egnough space on the X axis to appeaar in labyrinth 
        {
            for (int idxZ = 1; idxZ < cellLenghtZ - 1; idxZ++)
            // 0 and -1 on the Z axis are the empty sides.
            {
                if (stateDict[(idxX, idxZ)] == 0 && stateDict[(idxX + 1, idxZ)] == 0) // if two empty spaces are available in labyrint
                {
                    validSpawnPosList.Add(idxPosChocDict[(idxX, idxZ)]);
                }
            }
        }

        //GenerateLabyrinth Random number of chocolate bars to spawn
        if (ChocBarsMax <= validSpawnPosList.Count)
        {
            ChocBarsNumber = UnityEngine.Random.Range(1, ChocBarsMax + 1);
        }
        else //if maximum number of chocolate bars to spawn > as valis spawn positions
        {
            ChocBarsNumber = UnityEngine.Random.Range(1, validSpawnPosList.Count + 1);
        }

        // spawn ChocoleBar objects
        Cell ChocBar = chocCell;

        int chocBarsSpawned = 0;
        while(chocBarsSpawned < ChocBarsNumber)
        { 
            int chocPosIdx = UnityEngine.Random.Range(0, validSpawnPosList.Count);
            //Instanciate ChocolateBar Object 

            Instantiate(ChocBar, validSpawnPosList[chocPosIdx], ChocBar.transform.rotation);

            chocBarsSpawned++;
        }
        validSpawnPosList.Clear();
    }

    public bool ValidatePosition(int _idxX, int _idxZ)
	{
        try
        {
            // verify if the indexes are within the cell indexes
            if (stateDict[(_idxX, _idxZ)] == 1)
            {
                return true;
            }
        }
        catch
        {
            return false;
        }
        return true;
    }


    // Update is called once per frame
    void Update()
    {		
		// spawn new labyrinth(to ajust values if row values or percentage
	    // of free cells in labyrinth are changes in inspector)

        //***uncomment section for adjusting purposes***

  //      if (Input.GetKey(KeyCode.L))
		//{
		//	ClearLabyrinthValues();
		//	for (int tries = 0; tries < 100; tries++)
		//	{
		//		CreateCellList();
		//		GenerateLabyrinth();

		//		bool labyrinth = ValidateLabyrinth();

		//		if (labyrinth == true)
		//		{
		//			SpawnPillars();
		//			SpawnChocolate();
		//			break;
		//		}
		//		else
		//		{
		//			//restart process - generate new labyrinth
		//			ClearLabyrinthValues();
		//		}
		//	}
		//}
	}
}
