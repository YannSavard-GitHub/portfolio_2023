/*****************************************************************************
* Project: LevelEditorToolDev
* File   : Level.cs
* Date   : 10.02.2021
* Author : Yann Savard (YS)
*
* These coded instructions, statements, and computer programs contain
* proprietary information of the author and are protected by Federal
* copyright law. They may not be disclosed to third parties or copied
* or duplicated in any form, in whole or in part, without the prior
* written consent of the author.
*
* History:
* 10.02.2021 Created by  by Yann Savard (YS)
******************************************************************************/
using System;
using System.Collections.Generic;

namespace LevelEditorToolDev
{
    public partial class MainWindow
    {
        [Serializable]
        public class Level
        {
            public (int, int)[] dictKeys;
            public string[] dictValues;

            public (int, int)[] ConvertDictKeys(Dictionary<(int, int), string> dict)
            {
                dictKeys = new (int, int)[dict.Count];
                dict.Keys.CopyTo(dictKeys, 0);
                return dictKeys;
            }

            public string[] ConvertDictValues(Dictionary<(int, int), string> dict)
            {
                dictValues = new string[dict.Count];
                dict.Values.CopyTo(dictValues, 0);
                return dictValues;
            }
        }
    }
}


