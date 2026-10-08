on(construct){
   loop1:
   while(true)
   {
      while(true)
      {
         if(!ord("\x05"))
         {
            if(false)
            {
               §§goto(addr38b16);
            }
         }
         else
         {
            §§push("\t");
         }
         if(!ord(§§pop()))
         {
            break;
         }
         break loop1;
      }
      set(§§pop(),§§pop());
      §§goto(addr38c33);
   }
   addr38ba6:
   backgroundRenderer = "UI_BannerContainerBackground";
   set("\x16\x10\x12","UI_BannerContainerBorder");
   dragAndDrop = true;
   enabled = true;
   §§push("\x18\x07\x0e");
   §§push(true);
   if(getTimer() + 1)
   {
      set(§§pop(),§§pop());
      while(true)
      {
         highlightRenderer = "UI_BannerContainerHighLight";
         id = 1;
         margin = 1;
         set("\x1a\x1e\b",false);
         §§push("styleName");
         §§push("InventoryGridContainer");
         if(ord("\x07"))
         {
            break loop2;
         }
         setProperty(§§pop(), _X, §§pop());
         §§goto(addr38ba6);
         set(§§pop(),§§pop());
      }
      break loop2;
      addr38b16:
   }
   addr38c33:
   §§pop()();
}
