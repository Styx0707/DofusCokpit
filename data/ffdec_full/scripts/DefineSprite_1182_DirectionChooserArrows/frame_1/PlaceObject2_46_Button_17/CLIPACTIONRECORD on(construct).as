on(construct){
   while(true)
   {
      if(!(0x1F2F744E | 0x1F2F744E))
      {
         if(!ord("\b"))
         {
            break;
         }
      }
      else
      {
         §§push(94126608);
      }
      if(!(§§pop() + 1))
      {
         break;
      }
      while(true)
      {
         if(!getTimer())
         {
            setProperty(§§pop(), _X, §§pop());
            break;
         }
         backgroundDown = "ButtonTransparentUp";
         backgroundUp = "ButtonTransparentUp";
         enabled = true;
         icon = "DirectionChooserArrowT";
         label = "";
         §§push("selected");
         §§push(false);
         if(getTimer())
         {
            addr15f6:
            set(§§pop(),§§pop());
            set(§§constant(9),§§constant(10));
            set(§§constant(11),false);
            break;
         }
         setProperty(§§pop(), _X, §§pop());
      }
      return;
   }
   §§goto(addr15f6);
}
