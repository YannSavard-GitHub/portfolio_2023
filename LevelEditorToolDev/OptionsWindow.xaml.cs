/*****************************************************************************
* Project: LevelEditorToolDev
* File   : OptionsWindow.cs
* Date   : 20.02.2021
* Author : Yann Savard (YS)
*
* These coded instructions, statements, and computer programs contain
* proprietary information of the author and are protected by Federal
* copyright law. They may not be disclosed to third parties or copied
* or duplicated in any form, in whole or in part, without the prior
* written consent of the author.
*
* History:
* 27.02.2021 Created by  by Yann Savard (YS)

******************************************************************************/
using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;

namespace LevelEditorToolDev
{
    /// <summary>
    /// Interaction logic for OptionsWindow.xaml
    /// </summary>
    public partial class OptionsWindow : Window
    {
        private TextBox textBox;
        private SolidColorBrush solidColorBrush; // background color (when user's choices are valid)

        // for all user input, bool are true if input was successful
        private bool success1 = false; 
        private bool success2 = false;
        private bool success3 = false;
        private bool success4 = false;

        private int message = -1; //number of the messages.

        public OptionsWindow()
        {
            InitializeComponent();
            solidColorBrush= new SolidColorBrush(Color.FromArgb(0xFA, 0xAA, 1, 9));
        }

        private void OnTextBoxKeyDown(object sender, KeyEventArgs e)
        {
            //get values and verify their validity
            textBox = sender as TextBox;
            string str = textBox.Text;

            //if Enter is pressed
            if (e.Key == Key.Return)
            {
                switch (textBox.Tag)
                {
                    case "1":
                        message = 1;
                        VerifyDimensions(str);
                        break;
                    case "2":
                        message = 2;
                        VerifyHeight(str); 
                        break;
                    case "3":
                        message = 3;
                        VerifyPositionTop(str);
                        break;
                    case "4":
                        message = 4;
                        VerifyPositionLeft(str);
                        break;
                    default:
                        break;
                }
            }
		}

		private void AllMessages(int _message)
		{
			switch (_message)
			{
				case 1:
					MessageBox.Show("Ganzzahl zwischen 1 und 20 eingeben.",
                        "Falsche Angabe", MessageBoxButton.OK, MessageBoxImage.Information);
					textBox.Text = ""; break;
				case 2:
					MessageBox.Show($"Zahl zwischen {MainWindow.windowMinHeight.ToString("0000.00")} " +
                        $"und {SystemParameters.PrimaryScreenHeight.ToString("0000.00")} eingeben.",
                        "Falsche Angabe", MessageBoxButton.OK, MessageBoxImage.Information);
					textBox.Text = ""; break;
				case 3:
					MessageBox.Show($"Zahl zwischen {0} und " +
					    $"{(SystemParameters.PrimaryScreenHeight - MainWindow.savedWindow_Width).ToString("0000.00")} " +
                        $"eingeben.", "Falsche Angabe", MessageBoxButton.OK,
                        MessageBoxImage.Information);
					textBox.Text = "";
					break;
				case 4:
					MessageBox.Show(
						$"Zahl zwischen {0} und " +
						$"{(SystemParameters.PrimaryScreenHeight - MainWindow.windowMinHeight).ToString("0000.00")} " +
						$"eingeben.", "Falsche Angabe", MessageBoxButton.OK, MessageBoxImage.Information);
					textBox.Text = ""; break;
				default: break;
			}
		}

		private void VerifyDimensions(string _str)
        {
            int intValue;
            try
            {
                if (Int32.TryParse(_str, out intValue))
                {
                    if (intValue > 0 && intValue <= 20)
                    {
                        MainWindow.savedDimensionsLevelGrid = intValue;
                        success1 = true;
                        VerifySuccessAndCloseWindow();
                        return;
                    }
                }
            }
            catch (Exception)
            {         
            }
            AllMessages(1);
        }

        private void VerifyHeight(string _str)
        {
            double doubleValue;
            try
            {
                if (Double.TryParse(_str, out doubleValue))
                {
                    if (doubleValue < SystemParameters.PrimaryScreenHeight && doubleValue >
                        MainWindow.windowMinHeight)
                    {
                        MainWindow.savedWindow_Height = doubleValue;
                        success2 = true;
                        VerifySuccessAndCloseWindow();
                        return;
                    }
                }              
            }
            catch (Exception)
            {
            }
            AllMessages(2);
        }

        private void VerifyPositionTop(string _str)
        {
            double doubleValue;
            try
            {
                if (Double.TryParse(_str, out doubleValue))
                {
                    if (doubleValue > 0 && doubleValue <
                        SystemParameters.PrimaryScreenHeight -
                        MainWindow.savedWindow_Width)
                    {
                        MainWindow.savedWindow_Height = doubleValue;
                        success3 = true;
                        VerifySuccessAndCloseWindow();
                        return;
                    }      
                }
            }
            catch (Exception)
            {
            }
            AllMessages(3);
        }

        private void VerifyPositionLeft(string _str)
        {
            double doubleValue;
            try
            {
                if (Double.TryParse(_str, out doubleValue))
                {
                    if (doubleValue > 0 && doubleValue <
                        SystemParameters.PrimaryScreenWidth -
                        MainWindow.savedWindow_Width)
                    { 
                        MainWindow.savedWindow_Width = doubleValue;

                        //calculate ratio windowMinWidth from windowMinHeight 
                        //proportional equation to the one in OnSizeChanged Event in MainWindow.

                        MainWindow.windowMinWidth = 1 / (MainWindow.windowMinHeight / MainWindow.windowMinWidth *
                            MainWindow.windowMinHeight);
                        success4 = true;
                        VerifySuccessAndCloseWindow();
                        return;
                    }       
                }
            }
            catch (Exception)
            {
            }
            AllMessages(4);
        }

        private void VerifySuccessAndCloseWindow()
        {
            if (success1 && success2 && success3 && success4)
            {
                //reset success vars
                success1 = success2 = success3 = success4 = false;
                MessageBox.Show("Ihre Angabe wurden gespeichert. Clicken Sie auf " +
                    "dem Button ***Level generieren***, um das Level zu generieren.",
                    "Bestätigung", MessageBoxButton.OK, MessageBoxImage.Information);
                MainWindow.optionWindow.Close();
            }
        }

        private void OnOptionsWindowClosed(object sender, EventArgs e)
        {
            MainWindow.generateOptionWindowInstance();          
        }
    }
}

