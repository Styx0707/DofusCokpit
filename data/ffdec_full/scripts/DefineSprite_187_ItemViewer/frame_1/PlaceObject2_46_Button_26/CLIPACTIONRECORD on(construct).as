on(construct){
   while(true)
   {
      if(!(true and true))
      {
         if(!ord("\b"))
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
         icon = "Chaine";
         label = "";
         §§push("selected");
         §§push(false);
         if(!getTimer())
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr051a);
         }
      }
      set(§§pop(),§§pop());
      styleName = "FilterButton";
      break;
   }
   toggle = false;
   addr051a:
}
