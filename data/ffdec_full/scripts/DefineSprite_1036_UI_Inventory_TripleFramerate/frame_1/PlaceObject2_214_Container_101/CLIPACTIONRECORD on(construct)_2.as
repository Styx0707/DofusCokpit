on(construct){
   while(true)
   {
      if(false)
      {
         if(!ord("\x04"))
         {
            break;
         }
      }
      else
      {
         §§push("\b");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      backgroundRenderer = "UI_InventoryContainerBackground";
      set("\x16\x10\x12","");
      dragAndDrop = true;
      enabled = true;
      §§push("\x18\x07\x0e");
      §§push(true);
      if(!getTimer())
      {
         §§goto(addr1aedf);
      }
      break;
   }
   set(§§pop(),§§pop());
   highlightRenderer = "UI_InventoryContainerHighlight_TripleFramerate";
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr1aedf:
   getProperty(§§pop(), _X);
}
