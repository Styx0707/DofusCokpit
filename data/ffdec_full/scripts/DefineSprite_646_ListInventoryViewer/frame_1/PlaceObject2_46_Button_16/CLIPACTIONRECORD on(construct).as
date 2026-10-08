on(construct){
   while(true)
   {
      if(!(true and true))
      {
         if(!(true or true))
         {
            break;
         }
      }
      else
      {
         §§push("\x04");
      }
      if(ord(§§pop()))
      {
         backgroundDown = "ButtonToggleDown";
         backgroundUp = "ButtonToggleUp";
         enabled = true;
         icon = "FilterIcon11";
         label = "";
         §§push("selected");
         §§push(false);
         if(!ord("\x02"))
         {
            §§goto(addrd3d8);
         }
      }
      set(§§pop(),§§pop());
      §§push("styleName");
      §§push("FilterButton");
      break;
   }
   set(§§pop(),§§pop());
   toggle = true;
   addrd3d8:
   §§pop()(§§pop());
}
