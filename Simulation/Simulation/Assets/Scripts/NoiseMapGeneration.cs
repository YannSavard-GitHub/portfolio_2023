/*****************************************************************************
* Project: Simulation
* File   : NoiseMapGeneration.cs
* Date   : 22.10.2020
* Author : 	Jacob Stephan (JS)
*
* These coded instructions, statements, and computer programs contain
* proprietary information of the author and are protected by Federal
* copyright law. They may not be disclosed to third parties or copied
* or duplicated in any form, in whole or in part, without the prior
* written consent of the author.
*
* History:
* 22.10.2020	JS	Created
******************************************************************************/

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class NoiseMapGeneration : MonoBehaviour
{
    /// <summary>
    /// Calculates Perlin Noise map based on Params
    /// </summary>
    /// <param name="mapDepth">Y size</param>
    /// <param name="mapWidth">X Size</param>
    /// <param name="scale"> scale factor</param>
    /// <returns></returns>
    public float[,] GenerateNoiseMap(int mapDepth, int mapWidth, float scale)
    {

        float[,] noiseMap = new float[mapDepth, mapWidth];

        for (int zIndex = 0; zIndex < mapDepth; zIndex++)
        {
            for (int xIndex = 0; xIndex < mapWidth; xIndex++)
            {
                float sampleX = xIndex / scale;
                float sampleZ = zIndex / scale;

                //YS--------------------------------------- to add roughness to the terrain
                int variation = Random.Range(0, 2);
                float variation2 = Random.Range(0.01f, 0.15f);

                switch (variation)
				{
                    case 0:
                        noiseMap[zIndex, xIndex] = Mathf.PerlinNoise(sampleX, sampleZ); 
                        break;
                    case 1: 
                        noiseMap[zIndex, xIndex] = Mathf.PerlinNoise(sampleX + variation2, sampleZ); 
                        break;
                    case 2:
                        noiseMap[zIndex, xIndex] = Mathf.PerlinNoise(sampleX + variation2, sampleZ  ); 
                        break;
                }
                //YS-------------------------------------------------
            }
        }

        return noiseMap;
    }

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {

    }
}