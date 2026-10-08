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
         §§push("\x02");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      backgroundDown = "ButtonToggleDown";
      backgroundUp = "ButtonToggleUp";
      enabled = true;
      icon = "Loupe";
      §§push("label");
      §§push("");
      if(!ord("\x02"))
      {
         §§goto(addr68bcc);
      }
      break;
   }
   set(§§pop(),§§pop());
   selected = false;
   styleName = "FilterButton";
   toggle = true;
   addr68bcc:
   §§pop()(§§pop());
}
