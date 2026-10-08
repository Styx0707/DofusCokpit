on(construct){
   while(true)
   {
      if(!ord("\x06"))
      {
         if(!(0x35BB2588 | 0x35BB2588))
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
         if(!ord("\x06"))
         {
            duplicateMovieClip(§§pop(),§§pop(),§§pop());
         }
         backgroundDown = "ButtonPlusDown";
         backgroundUp = "ButtonPlusUp";
         enabled = true;
         icon = "";
         label = "";
         selected = false;
         §§push("styleName");
         §§push("OrangeButton");
         if(!(getTimer() + 1))
         {
            duplicateMovieClip(§§pop(),§§pop(),§§pop());
            §§goto(addr9f04);
         }
      }
      set(§§pop(),§§pop());
      §§push(§§constant(11));
      §§push(false);
      break;
   }
   set(§§pop(),§§pop());
   addr9f04:
}
