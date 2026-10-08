on(construct){
   loop2:
   while(true)
   {
      loop3:
      while(true)
      {
         if(!ord("\n"))
         {
            if(!(true or true))
            {
               while(true)
               {
                  set(§§pop(),§§pop());
                  wordWrap = false;
                  set("\x17\x07\x11",false);
                  §§push("\x17\b\x14");
                  §§push(false);
                  if(!getTimer())
                  {
                     setProperty(§§pop(), _X, §§pop());
                     §§goto(addr4318c);
                  }
                  else
                  {
                     §§goto(addr43264);
                  }
                  break loop3;
               }
               §§goto(addr43345);
               addr4315f:
            }
         }
         else
         {
            §§push(true);
         }
         var _temp_1 = §§pop();
         if(!(_temp_1 or _temp_1))
         {
            break;
         }
         break loop2;
      }
      set(§§pop(),§§pop());
      §§goto(addr4315f);
   }
   addr432b7:
   backgroundDown = "ButtonToggleDown";
   backgroundUp = "ButtonToggleUp";
   enabled = true;
   icon = "Loupe";
   label = "";
   §§push("selected");
   §§push(false);
   set(§§pop(),§§pop());
   styleName = "LightBrownItemViewer";
   toggle = false;
   cellRenderer = "ItemViewerItem";
   multipleSelection = false;
   §§push("rowHeight");
   §§push(20);
   if(!getTimer())
   {
      §§push(new §\§\§pop()§());
      while(true)
      {
         set(§§pop(),§§pop());
         showBaseEffects = false;
         set("\x17\b\x18",316);
         set("\x1b\r\x1c",false);
         set("\x1b\x16\x13",false);
         §§push("\x18\x06\x0f");
         §§push(false);
         if(!ord("\x0b"))
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr432b7);
         }
         §§goto(addr431d5);
      }
      addr43264:
   }
   addr4318c:
   set(§§pop(),§§pop());
   set("\x16\b\t",false);
   set("\x17\x05\x15",false);
   set("\x1a\t\x14",false);
   html = false;
   §§push("multiline");
   §§push(false);
   break loop3;
   setProperty(§§pop(), _X, §§pop());
   addr431d5:
   §§goto(addr43346);
   addr43345:
   setProperty(§§pop(), _X, §§pop());
   addr43346:
   set(§§pop(),§§pop());
}
