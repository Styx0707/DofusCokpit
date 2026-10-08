on(construct){
   while(true)
   {
      if(!(0x0187A30E & 0x0187A30E))
      {
         if(!ord("\x03"))
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(!§§pop())
      {
         while(true)
         {
            backgroundDown = "ButtonToggleDown";
            backgroundUp = "ButtonToggleUp";
            enabled = true;
            icon = "Loupe";
            §§push("label");
            §§push("");
            if(!(getTimer() + 1))
            {
               §§push(getProperty(§§pop(), _X));
            }
            set(§§pop(),§§pop());
            selected = false;
            styleName = "LightBrownItemViewer";
            toggle = false;
            set("\x1a\t\x14",false);
            html = false;
            §§push("multiline");
            §§push(false);
            if(!ord("\n"))
            {
               §§push(new §\§\§pop()§());
               break;
            }
            set(§§pop(),§§pop());
            text = "0";
            wordWrap = false;
            set("\x17\x07\x11",false);
            set("\x17\b\x14",false);
            §§push("showBaseEffects");
            §§push(false);
            if(!(getTimer() + 1))
            {
               continue;
            }
            §§push(new §\§\§pop()§());
         }
         §§goto(addr1453);
      }
      set(§§pop(),§§pop());
      break;
   }
   set("\x17\b\x18",316);
   set("\x1b\r\x1c",false);
   set("\x1b\x16\x13",false);
   set("\x18\x06\x0f",false);
   addr1453:
}
