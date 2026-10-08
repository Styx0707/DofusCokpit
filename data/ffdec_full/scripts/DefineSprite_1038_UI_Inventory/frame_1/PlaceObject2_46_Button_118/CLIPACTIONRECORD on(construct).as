on(construct){
   while(true)
   {
      if(false)
      {
         if(!(0x204E2804 & 0x204E2804))
         {
            break;
         }
      }
      else
      {
         §§push("\x02");
      }
      if(ord(§§pop()))
      {
         backgroundDown = "ButtonToggleDown";
         backgroundUp = "ButtonToggleUp";
         enabled = true;
         icon = "FilterIcon12";
         label = "";
         selected = false;
         §§push("styleName");
         §§push("FilterButton");
         if(false)
         {
            §§goto(addr409b);
         }
      }
      set(§§pop(),§§pop());
      §§push("toggle");
      §§push(true);
      break;
   }
   set(§§pop(),§§pop());
   addr409b:
   new §\§\§pop()§();
}
