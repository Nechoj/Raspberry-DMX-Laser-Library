<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?php
  // printing out php errors for debugging
  error_reporting (E_ALL | E_STRICT);
  ini_set ('display_errors' , 1);

  include 'modules/m_menu.php';
  include 'modules/m_books.php';
  $message0 = '';
  $message1 = '';
  $message2 = '';
  $message3 = '';
  $row = '';
  $dist = '';
?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <title>
      Library Management System
    </title>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link href="css/blitzer/jquery-ui-1.10.4.custom.css" rel="stylesheet" />
    <link rel="stylesheet" media="all" href="css/style_screen.css" />
    <link rel="stylesheet" media="only screen and (max-device-width:480px)" href="css/style_handheld.css" />
    <script src="js/jquery-1.10.2.js"></script>
    <script src="js/jquery-ui-1.10.4.custom.js"></script>
    <script>
        $(function() {
                $( "#tabs" ).tabs();
        });
    </script>
    <script type="text/javascript">
    function CheckSelection () {
    var sel_i = document.create_book.books.selectedIndex;
    if(sel_i > 0)
        var fields = document.create_book.books.options[sel_i].text.split(" // ");
        document.getElementsByName("title")[0].value = fields[0];
        document.getElementsByName("author")[0].value = fields[1];
    }
    </script>
  </head>
  <body>
    <div class="layoutPage">
      <div class="layoutPageHead">
        <div class="globalLogo left">
          Library Management System
        </div>
      </div>
      <div class="globalNavigationMain">
        <?php create_menu(); ?>
      </div>
      <div class="layoutPageBody">
        <div id="tabs">
          <ul>
            <li>
              <a href="#tabs-0">Detect Books</a>
            </li>
            <li>
              <a href="#tabs-1">Add Books</a>
            </li>
            <li>
              <a href="#tabs-2">Change Location of Books</a>
            </li>
            <li>
              <a href="#tabs-3">Delete Books</a>
            </li>
          </ul>
          <div id="tabs-0">
            <form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="post">
                <p>Make clear view of camera to shelf and press button Step 1</p>
                <p><a onclick="document.body.className = 'wait'"><input type="submit" name="button_step1" class="Button" value="Step 1"/></a></p>
                <?php 
                    if (isset($_POST['button_step1'])){
                        echo "<p>Rotate book by 90 degrees and then press button Step 2</p>\n";                
                        echo "<p><a onclick='document.body.className = \"wait\"'><input type='submit' name='button_step2' class='Button' value='Step 2'/></a></p>\n";
                    }
                ?>
            </form>
            <?php
                if (isset($_REQUEST["button_step1"])){ // if button_step1 was clicked on
                    set_parameter("Action", "Detect1"); // this parameter is then read by the laser_daemon process
                    while(get_parameter("Action") != "done"){
                        sleep(0.2);
                    }
                }
                if (isset($_REQUEST["button_step2"])){
                    set_parameter("Action", "Detect2"); // this parameter is then read by the laser_daemon process
                    while(get_parameter("Action") != "done"){
                        sleep(0.2);
                    }            
                    $row = get_parameter("row");
                    if ($row==0){
                        echo "\n<p>Book position not detected - try again, or, continue and enter book position data manually</p>\n";
                        echo "<form action='books.php#tabs-1' method='get'>\n";
                        echo "<p><input type='submit' name='button_continue' class='Button' value='Continue'/></p>\n";
                        echo "</form>\n";
                    }else{
                        header('Location: /books.php#tabs-1');
                        exit;
                    }
                }
            ?>
            <div class="Message">
                <p><?php echo $message0; ?></p>
            </div>
          </div>
          <div id="tabs-1">
            <p>
              1.) Select book from list, or, type in title and author:
            </p><?php 
                        if (isset($_REQUEST["button_sync"])){ // if button_sync was clicked: execute this function *before* the select list is being queried
                        $message = zotero_sync();
                        }
                        if (isset($_REQUEST["button_test"])){ // if button_test was clicked
                            laser_to_position($_POST['row'], $_POST['position']);    
                        }
                        if (isset($_REQUEST["button_off"])){ // if button_test was clicked
                            set_parameter("Action", "Stop"); // this parameter is then read by the laser_daemon process    
                        }
                        if (isset($_REQUEST["button_store"])){ // if button_store was clicked
                            $bookID = substr($_POST['books'], 2);
                            if(intval($bookID)>0){ // book has been selected
                                set_location($bookID, $_POST['row'], $_POST['position']);
                                $message = "location  for book with ID $bookID set";
                            }elseif(($_POST['title']!='') & ($_POST['author']!='') & ($_POST['row']!='') & ($_POST['position']!='')){
                                $bookID = create_book(html_entity_decode($_POST['title']),html_entity_decode($_POST['author']),$_POST['row'],$_POST['position']);
                                if(is_numeric($bookID)){
                                    $message1 = "book created with ID $bookID";
                                }else{
                                    $message1 = "creation failed";
                                }        
                            }else{
                                $message1 = "input parameter missing";
                            }
                        }
                    ?>
            <form name="create_book" action="<?php echo $_SERVER['PHP_SELF'] . '#tabs-1';?>" method="post" id="create_book">
              <p>
                <select name="books" class="DropDown" size="1" onchange="CheckSelection()">
                  <?php book_select(isset($_POST['books']) ? substr($_POST['books'], 2) : 0); ?>
                </select> <input type="submit" name="button_sync" class="Button" value="zotero sync" />
              </p>
              <p>
                <input type="text" class="Inputfield2" name="title" value="" /> title <!-- value is set in function CheckSelection() -->
              </p>
              <p>
                <input type="text" class="Inputfield2" name="author" value="" /> author <!-- value is set in function CheckSelection() -->
              </p>
              <hr style="margin-top:2em;"/>   
              <p>
                2.) Check whether laser is pointing to the requested book.<br />
                If not, try automatic detection again, or, change row and position manually
              </p>
              <p>
                <input type="text" class="Inputfield1" name="row" value="<?php echo isset($_POST['row']) ? htmlentities($_POST['row']) : get_parameter('row'); ?>" />
                row (top row is 1)
              </p>
              <p>
                <input type="text" class="Inputfield1" name="position" value="<?php echo isset($_POST['position']) ? htmlentities($_POST['position']) : get_parameter('dist_x'); ?>" />
                position (cm from left border)
              </p>
              <p>
                <input type="submit" name="button_test" class="Button" value="test position" /> <input type="submit" name="button_off" class="Button" value="laser off" />
              </p>
              <hr style="margin-top:2em;"/>  
              <p>
                3.) If everything OK:
              </p>
              <p>
                <input type="submit" name="button_store" class="Button" value="add book" />
              </p>
              <div class="Message">
                <?php echo $message1; ?>
              </div>
            </form>
          </div>
          <div id="tabs-2">
            <?php
                        if (isset($_POST['row2'])) {
                            $row = $_POST['row2'];
                            $dist = $_POST['dist2'];
                            if (isset($_REQUEST["button3"])){ // if button3 was clicked on
                                $bookID = substr($_POST['books2'], 2);
                                $pos = get_location($bookID);
                                $row = $pos['row'];
                                $dist = $pos['dist'];
                            }    
                            if (isset($_REQUEST["button4"])){ // if button4 was clicked on
                                if(($_POST['row2']!='') & ($_POST['dist2']!='')){
                                    $bookID = substr($_POST['books2'], 2);
                                    set_location($bookID, $_POST['row2'], $_POST['dist2']);
                                    $message2 = "location parameter set";
                                }else{
                                    $message2 =  "input parameter missing";
                                }
                            }
                        }
                    ?>
            <form action="<?php echo $_SERVER['PHP_SELF'] . '#tabs-2';?>" method="post">
              <p>
                <select name="books2" class="DropDown" size="1">
                  <?php book_select(isset($_POST['books2']) ? substr($_POST['books2'], 2) : 0); ?>
                </select> select title
              </p>
              <p>
                <input type="text" class="Inputfield1" name="row2" value="<?php echo isset($_POST['row2']) ? htmlspecialchars($row) : ''; ?>" /> row (top row is 1)
              </p>
              <p>
                <input type="text" class="Inputfield1" name="dist2" value="<?php echo isset($_POST['dist2']) ? htmlspecialchars($dist) : ''; ?>" /> position (cm from left border)
              </p>
              <p>
                <input type="submit" name="button3" class="Button" value="get location" /><input type="submit" name="button4" class="Button" value="set location" />
              </p>
              <div class="Message">
                <?php echo $message2; ?>
              </div>
            </form>
          </div>
          <div id="tabs-3">
            <?php
                        if (isset($_REQUEST["button2"])){ // if button2 was clicked on: create
                            $bookID = substr($_POST['books1'], 2);
                            $message3 = delete_book($bookID);
                        }
                    ?>
            <form action="<?php echo $_SERVER['PHP_SELF'] . '#tabs-3'; ?>" method="post">
              <p>
                <select name="books1" class="DropDown" size="1">
                  <?php book_select(isset($_POST['books1']) ? substr($_POST['books1'], 2) : 0); ?>
                </select> select title
              </p>
              <p>
                <input type="submit" name="button2" class="Button" value="delete" />
              </p>
              <div class="Message">
                <?php echo $message3; ?>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>