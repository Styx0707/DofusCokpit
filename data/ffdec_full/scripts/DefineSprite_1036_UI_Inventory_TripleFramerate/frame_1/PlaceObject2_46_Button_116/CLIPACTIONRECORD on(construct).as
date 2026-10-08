on(construct){
   while(true)
   {
      if(!ord("\t"))
      {
         if(false)
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
         backgroundDown = "ButtonToggleDown";
         backgroundUp = "ButtonToggleUp";
         enabled = true;
         icon = "FilterIcon12";
         label = "";
         selected = false;
         §§push("styleName");
         §§push("FilterButton");
         if(!(getTimer() + 1))
         {
            §§goto(addr8922);
         }
      }
      set(§§pop(),§§pop());
      §§push("toggle");
      §§push(true);
      break;
   }
   set(§§pop(),§§pop());
   addr8922:
   §§pop()(§§pop());
}
