on(construct){
   while(true)
   {
      if(!(0x1684E50B | 0x1684E50B))
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
            if(!getTimer())
            {
               §§push(getProperty(§§pop(), _X));
               break;
            }
            backgroundDown = "ButtonCraftDown";
            backgroundUp = "ButtonCraftUp";
            enabled = false;
            icon = "";
            label = "";
            selected = false;
            §§push("styleName");
            §§push("OrangeWhiteBorderButton");
            if(!ord("\x04"))
            {
               continue;
            }
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
         }
         §§goto(addr5e05c);
      }
      set(§§pop(),§§pop());
      set(§§constant(11),false);
      break;
   }
   addr5e05c:
}
