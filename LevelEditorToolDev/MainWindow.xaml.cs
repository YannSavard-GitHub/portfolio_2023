/*****************************************************************************
* Project: LevelEditorToolDev
* File   : MainWindow.cs
* Date   : 20.01.2021
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
* With parts taken from David Hackbarth, professor at the SAE Institute (DH)
******************************************************************************/
using Microsoft.Win32;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;

namespace LevelEditorToolDev
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {

        //Screen Dimensions
        public static double screenDimensions = SystemParameters.PrimaryScreenHeight;

        //window 
        public static double savedWindow_Width;
        public static double savedWindow_Height;
        public static double savedWindow_Left = 200; //(200= default value, if nothing saved)
        public static double savedWindowPos_Top = 200; //(200= default value, if nothing saved)

        public static double windowMinHeight;
        public static double windowMinWidth;

        //Option Window
        public static OptionsWindow optionWindow;
        public bool dontSaveVars = false; // true if Window and Grid vars values 
                                          // have already been saved from OptionsWindow class.
        // LevelGrid
        // number of RowDefinitions and ColumnDefinitions
        // number of rows and columns and always equal
        public static int currentDimensionsLevelGrid =8;//(default= 10 rows x 10 columns)
        public static int savedDimensionsLevelGrid;
        // images
        private Dictionary<(int, int), string> newDictLevel_ImagesIdxTags;
        private Dictionary<(int, int), string> DictLevel_ImagesIdxTags;

        // image from ElementGrid that will replace LevelGrid Images
        // activated through OnMouseLeftBottonDownElementGrid event.
        // default activeImage is set in method SetActiveImage()
        public Image activeImageLeft; // image activated with left click
        public Image activeImageRight; // image activated with right click
        public bool leftMouseIsDown { get; set; }
        public bool rightMouseIsDown { get; set; }
        public bool LastMouseButtonDownLeft; // true if last mouse button down was left button.
                                             // false if it was right botton

        // main folder
        private static readonly string folder = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
        private static readonly string levelEditorFiles_FOLDER = folder + "\\Level Editor Files";

        // project folder (for default and saved projects)
        private static string project_FOLDER = levelEditorFiles_FOLDER + "\\" + "Default Project"; //default project folder

        // image folder for each project
        private static readonly string levelImages_FOLDER = project_FOLDER + "\\" + "Level Images";  //default images folder

        // file names - to save files 
        private static string txt_NAME = project_FOLDER + "\\" + "DefaultProject.txt"; //default file name    
        private static string level_NAME = project_FOLDER + "\\" + "DefaultProject.level"; //default file name
        //private static string json_NAME = project_FOLDER + "\\" + "DefaultProject.json"; //default file name

        // name of file to open...
        private static string opened_level_NAME;

        // name of saved (saved as) file 
        private static string savedAs_level_NAME;

        private static Level _level; //for dictionary loaded from binary .level file in method LoadLevelFile

        //Menu
        public ICommand New { get; set; }
        public ICommand Open { get; set; }
        public ICommand Save { get; set; }

        public MainWindow()
        {
            InitializeComponent();

            //set optionWindow values
            windowMinHeight = LevelEditorWindow.MinHeight;
            windowMinWidth = LevelEditorWindow.MinWidth;

            //initialise 
         
            optionWindow = new OptionsWindow();
            newDictLevel_ImagesIdxTags = new Dictionary<(int, int), string>();
            DictLevel_ImagesIdxTags = new Dictionary<(int, int), string>();
            _level = new Level();
            
            //create files
            CreateTxtFile();
            CreateLevelFile();

            //set default value of saved vars
            //according to current values
            SetSavedWindowAndGridVars();

            //LevelGrid
            SetLevelGridVars();
            SetLevelGridImages();

            //ElementsGrid
            SetElementGridImages();

            //set default activated images
            SetActiveImages();

            //save level and configuration files
            SaveTxtFile(txt_NAME);
            SaveFileAsLevel(level_NAME);
            //SaveFileAsJson(json_NAME);
        }

        /// <summary>
        /// There are two active images, one for each Mouse button.
        /// This method activates this images.
        /// </summary>
        public void SetActiveImages()
        {
            Image newActImageLeft = new Image();
            var bitmap1 = new BitmapImage(new Uri($"{levelImages_FOLDER}\\Image-01.bmp", UriKind.Absolute));
            activeImageLeft = newActImageLeft;
            activeImageLeft.Source = bitmap1;
            activeImageLeft.Tag = "Image-01";

            Image newActImageRight = new Image();
            var bitmap2 = new BitmapImage(new Uri($"{levelImages_FOLDER}\\Image-00.bmp", UriKind.Absolute));
            activeImageRight = newActImageRight;
            activeImageRight.Source = bitmap2;
            activeImageRight.Tag = "Image-00";
        }

        public void SetSavedWindowAndGridVars()
        {
            if(!dontSaveVars)
            {
                //save LevelEditorWindow dimensions and positions
                savedWindow_Height = LevelEditorWindow.Height;
                savedWindow_Width = LevelEditorWindow.Width;
                savedWindow_Left = LevelEditorWindow.Left;
                savedWindowPos_Top = LevelEditorWindow.Top;
                savedDimensionsLevelGrid = currentDimensionsLevelGrid;
            }
        }

        public void GetSavedWindowAndGridVars()
        {
            //save LevelEditorWindow dimensions and positions
            LevelEditorWindow.Height = savedWindow_Height;
            LevelEditorWindow.Width = savedWindow_Width;
            LevelEditorWindow.Left = savedWindow_Left;
            LevelEditorWindow.Top = savedWindowPos_Top;
            currentDimensionsLevelGrid = savedDimensionsLevelGrid;
        }

        //text file 
        public void CreateTxtFile()                     
        {
            if (!File.Exists(txt_NAME))
            {
                File.WriteAllText(txt_NAME, $"initialWindowWidth,{LevelEditorWindow.Width},initialWindowHeight,{LevelEditorWindow.Height}," +
                $"savedWindow_Left,{LevelEditorWindow.Left},savedWindowPos_Top,{LevelEditorWindow.Top}," +
                $"dimensionsLevelGrid,{currentDimensionsLevelGrid}");
            }
        }

        public void SaveTxtFile(string _path)
        {
            SetSavedWindowAndGridVars();

            File.WriteAllText(_path,
                $"initialWindowWidth,{savedWindow_Width},initialWindowHeight,{savedWindow_Height}," +
                $"savedWindow_Left,{savedWindow_Left},savedWindowPos_Top,{savedWindowPos_Top}," +
                $"dimensionsLevelGrid,{currentDimensionsLevelGrid}");       
        }

        /// <summary>
        /// Load configuration text file and set Window and LevelGrid variables.
        /// </summary>
        public void LoadTxtFileSetVars(string _path)
        {
            if (File.Exists(_path))
            {
                string text = File.ReadAllText(_path);
                string[] parts = text.Split(',');

                //LevelEditorWindow variables
                string savedWindow_Width_Str = parts[1];
                string savedWindow_Height_Str = parts[3];
                string savedWindow_Left_Str = parts[5];
                string savedWindow_Top_Str = parts[7];
                //LevelGrid 
                string loadedDimensionsLevelGrid_Str = parts[9];

                //parse-out variables
                double savedWindow_Width_Double;
                double savedWindow_Height_Double;
                double savedWindow_Left_Double;
                double savedWindow_Top_Double;
                int savedDimensionsLevelGrid_int;

                //Width
                bool success = Double.TryParse(savedWindow_Width_Str, out savedWindow_Width_Double);
                if (success)
                {
                    LevelEditorWindow.Width = savedWindow_Width_Double;
                }
                //Height
                success = Double.TryParse(savedWindow_Height_Str, out savedWindow_Height_Double);
                if (success)
                {
                    LevelEditorWindow.Height = savedWindow_Height_Double;
                }
                //Left
                success = Double.TryParse(savedWindow_Left_Str, out savedWindow_Left_Double);
                if (success)
                {
                    LevelEditorWindow.Left = savedWindow_Left_Double;
                }
                //Top
                success = Double.TryParse(savedWindow_Top_Str, out savedWindow_Top_Double);
                if (success)
                {
                    LevelEditorWindow.Top = savedWindow_Top_Double;
                }
                //dimensions
                success = Int32.TryParse(loadedDimensionsLevelGrid_Str, out savedDimensionsLevelGrid_int);
                if (success)
                {
                    savedDimensionsLevelGrid = savedDimensionsLevelGrid_int;
                    if (savedDimensionsLevelGrid_int != currentDimensionsLevelGrid)
                    {// update currentDimensionsLevelGrid
                        currentDimensionsLevelGrid = savedDimensionsLevelGrid_int;

                    }
                }
            }
        }

        //binary .level file
        public void CreateLevelFile()
        {
            File.WriteAllText(level_NAME, "");
        }

        private void SaveFileAsLevel(string _path)
        {
            SetSavedWindowAndGridVars();
            Level _level = new Level(); //YS

            //set key and values arrays in _serializableDict
            _level.ConvertDictKeys(DictLevel_ImagesIdxTags); 
            _level.ConvertDictValues(DictLevel_ImagesIdxTags); 

            using (Stream stream = File.Open(_path, FileMode.Create))
            {
                var bf = new System.Runtime.Serialization.Formatters.Binary.BinaryFormatter();
                bf.Serialize(stream, (Level)_level);
                stream.Close();
            }
        }

        //.json files related methods not used in this project - for future use
        private void SaveFileAsJson(string _path)  // DH - YS
        {
            SetSavedWindowAndGridVars();
            Level _level = new Level(); //YS

            //set key and values arrays in _serializableDict
            _level.ConvertDictKeys(DictLevel_ImagesIdxTags); //YS
            _level.ConvertDictValues(DictLevel_ImagesIdxTags); //YS

            using (StreamWriter sWriter = File.CreateText(_path)) // DH - YS
            {
                JsonSerializer jSerializer = JsonSerializer.Create(); // DH - YS
                jSerializer.Serialize(sWriter, _level); // DH - YS
            }
        }

        private void LoadJsonFile(string _path) 
        {
            using (StreamReader sReader = File.OpenText(_path)) 
            {
                //serializing
                JsonSerializer js = JsonSerializer.Create(); 
                _level = (Level)js.Deserialize 
                    (sReader, typeof(Level)); 

                ReplaceLevelDict();
            }
            //replace images in LevelGrid according to new dictionary values
            SetLevelGridImages();
        }   
        
        private void LoadLevelFile(string _path)
        {
            using (Stream stream = File.Open(_path, FileMode.Open))
            {
                var bf = new System.Runtime.Serialization.Formatters.Binary.BinaryFormatter();
                _level = (Level)bf.Deserialize(stream);

                ReplaceLevelDict();
            }
            //replace images in LevelGrid according to new dictionary values
            SetLevelGridImages();    
        }

        // Menu events methods
        // Files handling
        private void OpenFile()
        {
            //get saved files names.
            opened_level_NAME = GetOpenFileName("Binary Files | *.level", "level");
            if (opened_level_NAME != project_FOLDER)
            {
                //.level file
                LoadLevelFile(opened_level_NAME);

                //get .txt configuration file with same name as .level file
                string txtFilepath = BinaryLevelToTxt(opened_level_NAME);

                //open .txt file and set vars
                LoadTxtFileSetVars(txtFilepath);

                //set LevelEditorWindow and LevelGrid variables
                SetSavedWindowAndGridVars();

                //set LevelGrid variables
                SetLevelGridVars();

                SetLevelGridImages();         // reset LevelGrid with grey background image.
                ReplaceLevelDict();           // update dictionary values 
                ReplaceAllLevelGridImages();  // update images in LevelGrid 
            }
        }

        public void SaveAndResetLevel()
        {
            //window
            GetSavedWindowAndGridVars();

            //LevelGrid
            SetLevelGridVars();
            SetLevelGridImages();

            //save level file in default folder path
            SaveFileAsLevel(level_NAME);         
        }

        private void OnOpenExecuted(object sender, ExecutedRoutedEventArgs e)
        {
            OpenFile();
        }

        private void SaveProject()
        {
            Console.WriteLine("Project saved.\n");
            SaveFileAsLevel(level_NAME);

            //convert .level path to .txt
            string txtPath = BinaryLevelToTxt(level_NAME);
            SaveTxtFile(txtPath);
        }

        /// <summary>
        /// convert .level to .txt
        /// </summary>
        /// <param name="_levelPath"></param> .level file path
        /// <returns></returns>
        private string BinaryLevelToTxt(string _levelPath)
        {
            //get file name from .level file path
            string[] levelPathSplit = _levelPath.Split('\\');
            string textpath_split = levelPathSplit[levelPathSplit.Length - 1];
            string textpath = textpath_split.Remove(textpath_split.Length - 6);

            //save text file with file name
            string textpath_txt = project_FOLDER + $"\\{textpath}.txt";
            return textpath_txt;
        }
        private string GetSavedFileName(string _fileExtension, string _defaultExtention)
        {    
            SaveFileDialog saveFileDialog = new SaveFileDialog();
            saveFileDialog.Filter = $"*{_fileExtension}";
            saveFileDialog.DefaultExt = _defaultExtention;

            saveFileDialog.InitialDirectory = project_FOLDER;

            bool? result = saveFileDialog.ShowDialog(); //DH
            if (result.HasValue && result.Value)
            {
                return saveFileDialog.FileName;
            }
            else
            {
                return project_FOLDER;
            }
        }

        private string GetOpenFileName(string _fileExtension, string _defaultExtention)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog();
            openFileDialog.Filter = $"*{_fileExtension}";
            openFileDialog.DefaultExt = _defaultExtention;

            openFileDialog.InitialDirectory = project_FOLDER;

            bool? result = openFileDialog.ShowDialog(); //DH
            if (result.HasValue && result.Value)
            {
                return openFileDialog.FileName;
            }
            else
            {
                return project_FOLDER;
            }
        }

        private void OnSaveAsClick(object sender, RoutedEventArgs e)
        {
            //savedAs_txt_NAME= GetSavedFileName("Text Files | *.txt", "txt");
            savedAs_level_NAME = GetSavedFileName("Binary Files | *.level", "level");

            if (savedAs_level_NAME != project_FOLDER)
            {
                //replace default file name
                level_NAME = savedAs_level_NAME;
                //convert .level path to .txt
                string txtPath = BinaryLevelToTxt(savedAs_level_NAME);

                //save .level and .txt files
                SaveFileAsLevel(savedAs_level_NAME);
                SaveTxtFile(txtPath);
                //replace default file name
                txt_NAME = txtPath;
            }
        }

        //Images
        public void ReplaceLevelDict()
        {
            //Replace DictLevel_ImagesIdxTags values 
            //by values in _dictConverter.dictValues
            int dictCount = _level.dictKeys.Length;

            DictLevel_ImagesIdxTags.Clear();

            for (int i = 0; i < dictCount; i++)
            {
                DictLevel_ImagesIdxTags[_level.dictKeys[i]] = _level.dictValues[i];
            }
        }
        private void SetLevelGridVars()
        {
            LevelGrid.RowDefinitions.Clear();
            LevelGrid.ColumnDefinitions.Clear();
            for (int i = 0; i < currentDimensionsLevelGrid; i++)
            {
                //add RowDefinitions
                RowDefinition rowDef = new RowDefinition();
                rowDef.Height = new GridLength(1.0, GridUnitType.Star);
                LevelGrid.RowDefinitions.Add(rowDef);
                //add ColumnDefinitions
                ColumnDefinition columnDef = new ColumnDefinition();
                columnDef.Width = new GridLength(1.0, GridUnitType.Star);
                LevelGrid.ColumnDefinitions.Add(columnDef);
            }
        }

        /// <summary>
        /// Add Background images to the LevelGrid and 
        /// add images to the DictLevel_ImagesIdxTags
        /// </summary>
        private void SetLevelGridImages()
        {
            if(LevelGrid.Children.Count > 0) LevelGrid.Children.Clear();

            for (int i = 0; i < currentDimensionsLevelGrid; i++)
            {
                for (int j = 0; j < currentDimensionsLevelGrid; j++)
                {
                    Image newImage = new Image();
                    var bitmap = new BitmapImage
                        (new Uri($"{levelImages_FOLDER}\\Image-00.bmp", UriKind.Absolute));
                    newImage.Source = bitmap;
                    newImage.Stretch = Stretch.UniformToFill;
                    LevelGrid.Children.Add(newImage);
                    newImage.SetValue(Grid.RowProperty, i);
                    newImage.SetValue(Grid.ColumnProperty, j);
                    string name = "LevelImage" + i.ToString() + j.ToString();
                    newImage.Name = name;
                    newImage.Tag = "Image-00";
                    newImage.SetValue(Grid.ColumnSpanProperty, 1);
                    newImage.HorizontalAlignment = HorizontalAlignment.Center;
                    newImage.VerticalAlignment = VerticalAlignment.Center;
                    newImage.MouseLeftButtonDown += OnMouseLeftBottonDownLevelGrid;
                    newImage.MouseRightButtonDown += OnMouseRightBottonDownLevelGrid;
                    newImage.MouseEnter += OnMouseEnter;
                    try
                    { 
                        //when new project is loaded - set new source with new dictionary values
                        DictLevel_ImagesIdxTags[(i, j)] = DictLevel_ImagesIdxTags[(i,j)];
                        bitmap = new BitmapImage(new Uri($"{levelImages_FOLDER}\\" +
                            $"{DictLevel_ImagesIdxTags[(i, j)]}.bmp", UriKind.Absolute));
                        newImage.Source = bitmap;
                    }
                    catch (Exception)
                    {
                        //at program start
                        DictLevel_ImagesIdxTags.Add((i, j), newImage.Tag.ToString());
                    }      
                }
            }
        }

        /// <summary>
        /// This method adds the elements images from the levelImages_FOLDER 
        /// to the Element Grid
        /// </summary>
        private void SetElementGridImages()
        {
            //create image and set its attributes
            string ImageName;
            for (int i = 0; i < ElementsGrid.RowDefinitions.Count; i++)
            {
                for (int j = 0; j < ElementsGrid.ColumnDefinitions.Count; j++)
                {
                    Image newImage = new Image();
                    //the numbers in all ElementsGrid image NAMES is the index 
                    //of their source image in levelImages_FOLDER  
                    ImageName = "Image-" + i.ToString() + j.ToString();                    
                    var bitmap2 = new BitmapImage(new Uri
                           ($"{levelImages_FOLDER}\\{ImageName}.bmp", UriKind.Absolute));

                    newImage.Source = bitmap2;
                    newImage.Stretch = Stretch.UniformToFill;
                    ElementsGrid.Children.Add(newImage);
                    newImage.SetValue(Grid.RowProperty, i);
                    newImage.SetValue(Grid.ColumnProperty, j);
                    string tag = "Image-" + i.ToString() + j.ToString();

                    //the numbers in all ElementsGrid image TAGS is 
                    //also the index of the source image in levelImages_FOLDER    
                    newImage.Tag = tag;
                    newImage.SetValue(Grid.ColumnSpanProperty, 1);
                    newImage.HorizontalAlignment = HorizontalAlignment.Center;
                    newImage.VerticalAlignment = VerticalAlignment.Center;
                    newImage.MouseLeftButtonDown += OnMouseLeftBottonDownElementGrid;
                    newImage.MouseRightButtonDown += OnMouseRightBottonDownElementGrid;
                    newImage.MouseEnter += OnMouseEnter;
         
                    newDictLevel_ImagesIdxTags.Add((i, j), newImage.Tag.ToString());
                }
            }
        
        
        }

        //Replace LevelGrid images 
        private void ReplaceAllLevelGridImages()
        {
            //change image sources of Levelgrid with the new values of DictElements_ImagesIdxTags.
            string ImageName = "";
            for (int i = 0; i < currentDimensionsLevelGrid; i++)
            {
                for (int j = 0; j < currentDimensionsLevelGrid; j++)
                {
                    //get image name
                    foreach (Image image in LevelGrid.Children)
                    {
                        ImageName = "LevelImage" + i.ToString() + j.ToString();
                        if (image.Name == ImageName)
                        {
                            //get tag from Dictionary
                            string Imagetag= DictLevel_ImagesIdxTags[(i, j)];
                            var bitmap3 = new BitmapImage(new Uri($"{levelImages_FOLDER}\\{Imagetag}.bmp", UriKind.Absolute));
                            //change image source and tag
                            image.Source = bitmap3;
                            image.Tag = Imagetag;
                            break;
                        }
                    }
                }
            }
        }

        /// <summary>
        /// Replace the clicked Image's Source
        /// </summary>
        /// <param name="sender"></param> Image from Level that will be replaced
        /// <param name="_click"></param> click button (left "L" or right "R")
        private void ReplaceLevelGridImage(object sender, bool _LastMouseButtonDownLeft)
        {
            Image temporaryImage;
            if(_LastMouseButtonDownLeft == true)
            {
                temporaryImage = activeImageLeft;
                leftMouseIsDown = true;
                rightMouseIsDown = false;
                LastMouseButtonDownLeft = true;
            }
            else
            {
                temporaryImage = activeImageRight;
                rightMouseIsDown = true;
                leftMouseIsDown = false;
                LastMouseButtonDownLeft = false;
            }

            Image image = (Image)sender;

            //replace image source 
            image.Source = temporaryImage.Source;
            image.Tag= temporaryImage.Tag;

            // get column and row of LevelGrid Image to be replaced
            int idxX = (int)image.GetValue(Grid.RowProperty);
            int idxY = (int)image.GetValue(Grid.ColumnProperty);

            //replace value in dictionary DictIndexImage    
            DictLevel_ImagesIdxTags[(idxX, idxY)] = image.Tag.ToString();
            //add method (just the images of LevelGrid have the method MouseLeftButtonDown)
            image.MouseLeftButtonDown += OnMouseLeftBottonDownLevelGrid;
            image.MouseRightButtonDown += OnMouseRightBottonDownLevelGrid;
        }

        //mouse event handling
        private void OnMouseLeftBottonDownLevelGrid(object sender, MouseButtonEventArgs e)
        {
            LastMouseButtonDownLeft = true;
            ReplaceLevelGridImage(sender, LastMouseButtonDownLeft);
        }

        private void OnMouseRightBottonDownLevelGrid(object sender, MouseButtonEventArgs e)
        {
            LastMouseButtonDownLeft = false;
            ReplaceLevelGridImage(sender, LastMouseButtonDownLeft);
        }

        private void OnMouseLeftBottonDownElementGrid(object sender, MouseButtonEventArgs e)
        {
            //replace activeImageLeft and ImageLeftClick.Source 
            Image im = (Image)sender;
            activeImageLeft = im;
            ImageLeftClick.Source = activeImageLeft.Source;

            leftMouseIsDown = true;
            rightMouseIsDown = false;
            LastMouseButtonDownLeft = true;
        }

        private void OnMouseRightBottonDownElementGrid(object sender, MouseButtonEventArgs e)
        {
            //replace activeImageRight and ImageRightClick.Source 
            Image im = (Image)sender;
            activeImageRight = im;
            ImageRightClick.Source = activeImageRight.Source;

            rightMouseIsDown = true;
            leftMouseIsDown = false;
            LastMouseButtonDownLeft = false; //(right button is down)
        }

        private void OnMouseEnter(object sender, MouseEventArgs e)
        {
            try
            {
                Image image = (Image)sender;
                if (LastMouseButtonDownLeft == true) // left button was down
                {
                    if ((image.Parent == LevelGrid && leftMouseIsDown == true))
                    {
                        ReplaceLevelGridImage(sender, LastMouseButtonDownLeft);
                    }
                }
                else if(!LastMouseButtonDownLeft) // right button was down
                {
                    if ((image.Parent == LevelGrid && rightMouseIsDown == true))
                    {
                        ReplaceLevelGridImage(sender, LastMouseButtonDownLeft);
                    }
                }
            }
            catch (Exception)
            {
            }
        } 
        
        private void OnMouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            leftMouseIsDown = false;
            LastMouseButtonDownLeft = true;
        }

        private void OnMouseRightButtonUp(object sender, MouseButtonEventArgs e)
        {
            rightMouseIsDown = false;
            LastMouseButtonDownLeft = false;
        }

        /// <summary>
        /// To ajust window size proportionally when the window is ajusted.
        /// </summary>
        /// <param name="sender"></param> not used
        /// <param name="e"></param> SizeChangedEventArgs Event - window changed
        private void OnSizeChanged(object sender, SizeChangedEventArgs e)
        {
            double heightRatio = (savedWindow_Height / savedWindow_Width);
     
            if (e.WidthChanged)
            {
                LevelEditorWindow.Height= heightRatio * LevelEditorWindow.Width;
            }
            else if(e.HeightChanged)
            {  
                LevelEditorWindow.Width = 1/heightRatio * LevelEditorWindow.Height;
            }
        }

        private void OnLocationChangedWindow(object sender, EventArgs e)
        {
            savedWindow_Left = LevelEditorWindow.Left;
            savedWindowPos_Top = LevelEditorWindow.Top;
        }

        private void OnSaveCommandExecuted(object sender, ExecutedRoutedEventArgs e)
        {
            SaveProject();
        }

        private void OnOptionsClick(object sender, RoutedEventArgs e)
        {
            if(!optionWindow.IsActive)
            {
                optionWindow.ShowDialog();
                optionWindow.Top = LevelEditorWindow.Top + LevelEditorWindow.Top * 0.05f;
                optionWindow.Left = LevelEditorWindow.Left + LevelEditorWindow.Left * 0.2f;
            } 
        }

        // when option window closes, this method generated a new inactive window 
        public static void generateOptionWindowInstance()
        {
            OptionsWindow newOptionWindow = new OptionsWindow();
            optionWindow = newOptionWindow;
        }

        private void OnLevelEditorWidowClosed(object sender, EventArgs e)
        {//close option window.
            if (optionWindow.IsActive)
            {

                optionWindow.Close();
            }
            Application.Current.Shutdown();
        }

        private void OnNewExecuted(object sender, ExecutedRoutedEventArgs e)
        {
            SaveAndResetLevel();
        }
    }
}


