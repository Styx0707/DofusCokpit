on(construct){
   while(true)
   {
      if(false)
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x07");
      }
      if(ord(§§pop()))
      {
         backgroundDown = "ButtonToggleDown";
         backgroundUp = "ButtonToggleUp";
         enabled = true;
         icon = "Loupe";
         label = "";
         §§push("selected");
         §§push(false);
         if(!getTimer())
         {
            §§goto(addr19ff0);
         }
      }
      set(§§pop(),§§pop());
      styleName = "FilterButton";
      break;
   }
   toggle = true;
   addr19ff0:
   §§pop()();
}
