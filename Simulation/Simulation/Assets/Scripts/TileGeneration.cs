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


[System.Serializable]
public class TerrainType
{
    public string name;
    public float height;
    public Color color;
}

[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public class TileGeneration : MonoBehaviour
{
    [SerializeField]
    private TerrainType[] terrainTypes;

    public NoiseMapGeneration noiseMapGeneration;

    [SerializeField]
    private MeshRenderer tileRenderer;

    [SerializeField]
    private MeshFilter meshFilter;

    [SerializeField]
    private MeshCollider meshCollider;

    public float mapScale = 1;
    public float heightMod = 1;

    public AnimationCurve curve;

    public int xSize = 16;
    public int zSize = 16;

    // Start is called before the first frame update
    void Start()
    {
        GenerateMesh();
        GenerateTile();
    }

    void GenerateMesh()
    {
        this.meshFilter.mesh = new Mesh();

        Vector3[] vertices = new Vector3[((xSize + 1) * (zSize + 1))];
        Vector2[] uv = new Vector2[vertices.Length];


        for (int z = 0, i = 0; z <= zSize; z++)
        {
            for (int x = 0; x <= xSize; x++, i++)
            {
                vertices[i] = new Vector3(x, 0, z);
                uv[i] = new Vector2(x / (float)xSize, z / (float)zSize);

            }
        }

        this.meshFilter.mesh.vertices = vertices;

        int[] triangles = new int[zSize * xSize * 6];
        for (int ti = 0, vi = 0, z = 0; z < zSize; z++, vi++)
        {
            for (int x = 0; x < xSize; x++, ti += 6, vi++)
            {
                triangles[ti] = vi;
                triangles[ti + 3] = triangles[ti + 2] = vi + 1;
                triangles[ti + 4] = triangles[ti + 1] = vi + xSize + 1;
                triangles[ti + 5] = vi + xSize + 2;
            }
        }

        this.meshFilter.mesh.triangles = triangles;
        this.meshFilter.mesh.uv = uv;
    }

    void GenerateTile()
    {
        Vector3[] meshVertices = this.meshFilter.mesh.vertices;

        //berechne von den Map Dimensionen anhand der Mesh vertices anzahl
        int tileDepth = (int)Mathf.Sqrt(meshVertices.Length);
        int tileWidth = tileDepth;

        //offset berechnen
        float[,] heightmap = this.noiseMapGeneration.GenerateNoiseMap(   
                             tileDepth, tileWidth, this.mapScale);
        

        int vertexIndex = 0;
        for (int zIndex = 0; zIndex < tileDepth; zIndex++)
        {
            for (int xIndex = 0; xIndex < tileWidth; xIndex++)
            {
                float height = heightmap[zIndex, xIndex];
                Vector3 vertex = meshVertices[vertexIndex];

                meshVertices[vertexIndex] = new Vector3(
                    vertex.x,
                   curve.Evaluate(height) * heightMod,
                    vertex.z);
                vertexIndex++;
            }
        }

        // Mesh Updaten!
        this.meshFilter.mesh.vertices = meshVertices;
        this.meshFilter.mesh.RecalculateBounds();
        this.meshFilter.mesh.RecalculateNormals();
        this.meshFilter.mesh.RecalculateTangents();

        // Collider updaten
        this.meshCollider.sharedMesh = meshFilter.mesh;

        //texture Updaten!
        Texture2D tileTexture = BuildTexture(heightmap);
        this.tileRenderer.material.mainTexture = tileTexture;

    }

    private Texture2D BuildTexture(float[,] heightmap)
    {
        int tileDepth = heightmap.GetLength(0);
        int tileWidth = heightmap.GetLength(1);

        Color[] colorMap = new Color[tileDepth * tileWidth];
        for (int zIndex = 0; zIndex < tileDepth; zIndex++)
        {
            for (int xIndex = 0; xIndex < tileWidth; xIndex++)
            {
                int cIndex = zIndex * tileWidth + xIndex;
                float height = heightmap[zIndex, xIndex];


                foreach (TerrainType terrainType in terrainTypes)
                {
                    if (height < terrainType.height)
                    {
                        colorMap[cIndex] = terrainType.color;
                        break;                      
                    }
                }
                //colorMap[cIndex] = Color.Lerp(terrainType.color, Color.white, height);
            }
        }

        Texture2D tileTexture = new Texture2D(tileWidth, tileDepth);
        tileTexture.wrapMode = TextureWrapMode.Clamp;
        tileTexture.SetPixels(colorMap);
        tileTexture.Apply();

        return tileTexture;
    }

    // Update is called once per frame
    void Update()
    {
       
    }
}