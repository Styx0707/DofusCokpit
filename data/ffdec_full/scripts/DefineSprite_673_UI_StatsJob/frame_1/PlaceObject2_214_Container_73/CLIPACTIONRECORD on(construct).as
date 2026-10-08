on(construct){
   while(true)
   {
      if(!(true and true))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x0b");
      }
      if(ord(§§pop()))
      {
         backgroundRenderer = "UI_StatsJobContainerBackground";
         set("\x16\x10\x12","UI_StatsJobContainerBorder");
         dragAndDrop = false;
         enabled = true;
         set("\x18\x07\x0e",true);
         §§push("highlightRenderer");
         §§push("UI_StatsJobContainerHighlight");
         if(!ord("\x05"))
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            §§goto(addr10e6f);
         }
      }
      set(§§pop(),§§pop());
      §§push("id");
      §§push(1);
      break;
   }
   set(§§pop(),§§pop());
   margin = 0;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr10e6f:
}
